# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import logging

from django import forms
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import (
    ObjectDoesNotExist,
    ValidationError,
    ImproperlyConfigured,
)
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, get_language, ugettext

from aldryn_apphooks_config.utils import setup_config
from app_data import AppDataForm
from cms import __version__ as cms_version
from cms.models import Page
from distutils.version import LooseVersion
from emailit.api import send_mail
from multiupload.fields import MultiFileField
from parler.forms import TranslatableModelForm
from unidecode import unidecode


from .models import (
    JobApplication, JobApplicationAttachment, JobCategory, JobOpening,
    JobsConfig, JobListPlugin, JobCategoriesPlugin)
from .utils import namespace_is_apphooked

SEND_ATTACHMENTS_WITH_EMAIL = getattr(
    settings, 'ALDRYN_JOBS_SEND_ATTACHMENTS_WITH_EMAIL', True)
DEFAULT_SEND_TO = getattr(settings, 'ALDRYN_JOBS_DEFAULT_SEND_TO', None)

logger = logging.getLogger(__name__)


class AutoAppConfigFormMixin(object):
    """
    If there is only a single AppConfig to choose, automatically select it.
    """
    def __init__(self, *args, **kwargs):
        super(AutoAppConfigFormMixin, self).__init__(*args, **kwargs)
        if 'app_config' in self.fields:
            # if has only one choice, select it by default
            if self.fields['app_config'].queryset.count() == 1:
                self.fields['app_config'].empty_label = None


class AutoSlugForm(TranslatableModelForm):
    """
    Generates slugs and ensures that the slug is unique.
    """
    slug_field = 'slug'
    slugified_field = None

    def clean(self):
        super(AutoSlugForm, self).clean()

        if not self.data.get(self.slug_field):
            # We cannot modify self.data directly since it is immutable
            raw_data = self.data.copy()
            # add to self.data in order to show generated slug in the
            # form in case of an error
            slug = self.generate_slug()
            raw_data[self.slug_field] = slug
            self.cleaned_data[self.slug_field] = slug
            # Copy modifications back to self.data
            self.data = raw_data
        else:
            slug = self.cleaned_data[self.slug_field]
        language_code = self.get_language_code()
        # validate uniqueness
        conflict = self.get_slug_conflict(slug=slug, language=language_code)
        if conflict:
            self.report_error(conflict=conflict)

        return self.cleaned_data

    def generate_slug(self):
        content_to_slugify = self.cleaned_data.get(self.slugified_field, '')
        return slugify(unidecode(content_to_slugify))

    def get_language_code(self):
        try:
            language_code = self.instance.get_current_language()
        except ObjectDoesNotExist:
            language_code = get_language()
        return language_code

    def get_slug_conflict(self, slug, language):
        app_config_filter = self.get_app_config_filter()
        conflicts = (
            self._meta.model
                      .objects
                      .language(language)
                      .filter(app_config_filter)
                      .translated(language, slug=slug)
        )
        if self.instance.pk:
            conflicts = conflicts.exclude(pk=self.instance.pk)

        try:
            return conflicts.get()
        except self._meta.model.DoesNotExist:
            return self._meta.model.objects.none()

    def report_error(self, conflict):
        address = '<a href="%(url)s" target="_blank">%(label)s</a>' % {
            'url': conflict.get_absolute_url(),
            'label': _('the conflicting object')}
        error_message = (
            _('Conflicting slug. See %(address)s.') % {
                'address': address
            }
        )
        self.append_to_errors(field='slug', message=mark_safe(error_message))

    def append_to_errors(self, field, message):
        try:
            self._errors[field].append(message)
        except KeyError:
            self._errors[field] = self.error_class([message])

    def is_edit_action(self):
        return self.instance.pk is not None

    def validate_field_uniqueness_with_app_config(self, field_name,
                                                  error_message):
        """
        Validates uniqueness of field_name against app_config, if field is not
        valid - adds error_message to form errors.
        Returns True if field is unique, False otherwise.
        """
        field = self.cleaned_data.get(field_name, u'')
        language = self.get_language_code()
        app_config_filter = self.get_app_config_filter()
        qs = (self._meta.model.objects
                              .exclude(pk=self.instance.pk)
                              .language(language)
                              .filter(app_config_filter))
        # validate uniqueness
        if not field:
            # do not validate, for some reasons field data is not there,
            # most likely there is another validation error
            found = 0
        else:
            # since querysets are lazy database lookup would be evaluated
            # only if bool(field) is True.
            # .translated accepts key word arguments not Q objects.
            found = qs.translated(language, **{field_name: field}).count()

        if found > 0:
            self.append_to_errors(field_name, error_message)
        return found == 0


class JobCategoryAdminForm(AutoAppConfigFormMixin, AutoSlugForm):

    slugified_field = 'name'

    class Meta:
        model = JobCategory
        fields = ['name', 'slug', 'supervisors', 'app_config']

    def get_app_config_filter(self):
        """
        If there is app_config, returns a filter limiting queryset to
        objects in same app_config, otherwise, returns empty filter.
        """
        if 'app_config' in self.cleaned_data:
            app_config = self.cleaned_data['app_config']
            return Q(app_config=app_config)
        return Q()

    def clean(self):
        super(JobCategoryAdminForm, self).clean()
        error_message = _(
            'Category with that name already exists for selected app_config.')
        self.validate_field_uniqueness_with_app_config('name', error_message)
        return self.cleaned_data


class JobOpeningAdminForm(AutoSlugForm):

    slugified_field = 'title'

    class Meta:
        model = JobOpening
        fields = [
            'title',
            'slug',
            'lead_in',
            'category',
            'is_active',
            'can_apply',
            'publication_start',
            'publication_end'
        ]

        if LooseVersion(cms_version) < LooseVersion('3.0'):
            fields.append('content')

    def __init__(self, *args, **kwargs):
        super(JobOpeningAdminForm, self).__init__(*args, **kwargs)

        # small monkey patch to show better label for categories
        def label_from_instance(category_object):
            return "{0} / {1}".format(
                category_object.app_config,
                category_object
            )
        try:
            self.fields['category'].label_from_instance = label_from_instance
        except KeyError:
            # When the form is invoked by the render_model template tag with a
            # list of explicitly set fields, category might not be present.
            pass

    def get_app_config_filter(self):
        """
        If there is a category, returns a filter limiting the queryset to
        objects in the same app_config, otherwise, returns empty filter.
        """
        if 'category' in self.cleaned_data:
            app_config = self.cleaned_data['category'].app_config
            return Q(category__app_config=app_config)
        return Q()

    def clean(self):
        super(JobOpeningAdminForm, self).clean()
        error_message = _(
            'Opening with that title already exists for selected category.')
        self.validate_field_uniqueness_with_app_config('title', error_message)
        return self.cleaned_data


class JobApplicationForm(forms.ModelForm):
    FIVE_MEGABYTES = 1024 * 1024 * 5
    attachments = MultiFileField(
        max_num=getattr(settings, 'ALDRYN_JOBS_ATTACHMENTS_MAX_COUNT', 5),
        min_num=getattr(settings, 'ALDRYN_JOBS_ATTACHMENTS_MIN_COUNT', 0),
        max_file_size=getattr(
            settings, 'ALDRYN_JOBS_ATTACHMENTS_MAX_FILE_SIZE', FIVE_MEGABYTES),
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.job_opening = kwargs.pop('job_opening')
        if not hasattr(self, 'request') and kwargs.get('request') is not None:
            self.request = kwargs.pop('request')
        super(JobApplicationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = JobApplication
        fields = [
            'salutation',
            'first_name',
            'last_name',
            'email',
            'cover_letter',
        ]

    def save(self, commit=True):
        super(JobApplicationForm, self).save(commit=False)
        self.instance.job_opening = self.job_opening

        if commit:
            self.instance.save()

        for attachment in self.cleaned_data['attachments']:
            att = JobApplicationAttachment(
                application=self.instance, file=attachment)
            att.save()

        # additional actions while applying for the job
        try:
            self.send_confirmation_email()
        except:
            # We're handling ANY exception here because we don't want to
            # prevent the form from ultimately getting saved here.
            logger.exception('Could not send a confirmation email!')

        try:
            self.send_staff_notifications()
        except:
            # We're handling ANY exception here because we don't want to
            # prevent the form from ultimately getting saved here.
            logger.exception('Could not send a staff notifications!')

        return self.instance

    def send_confirmation_email(self):
        context = {'job_application': self.instance}
        send_mail(recipients=[self.instance.email],
                  context=context,
                  template_base='aldryn_jobs/emails/confirmation')

    def send_staff_notifications(self):
        recipients = self.instance.job_opening.get_notification_emails()
        if DEFAULT_SEND_TO:
            recipients += [DEFAULT_SEND_TO]
        admin_change_form = reverse(
            'admin:%s_%s_change' % (self._meta.model._meta.app_label,
                                    self._meta.model._meta.module_name),
            args=(self.instance.pk,)
        )

        context = {
            'job_application': self.instance,
        }
        # make admin change form url available
        if hasattr(self, 'request'):
            context['admin_change_form_url'] = self.request.build_absolute_uri(
                admin_change_form)

        kwargs = {}
        if SEND_ATTACHMENTS_WITH_EMAIL:
            attachments = self.instance.attachments.all()
            if attachments:
                kwargs['attachments'] = []
                for attachment in attachments:
                    attachment.file.seek(0)
                    kwargs['attachments'].append(
                        (os.path.split(
                            attachment.file.name)[1], attachment.file.read(),))
        send_mail(recipients=recipients,
                  context=context,
                  template_base='aldryn_jobs/emails/notification', **kwargs)


class JobsConfigForm(AppDataForm):
    pass


class AppConfigPluginFormMixin(object):
    config_model = JobsConfig

    def __init__(self, *args, **kwargs):
        # config_model should be configured before using this mixin
        if self.config_model is None:
            raise ImproperlyConfigured(
                ugettext('Cannot work properly when config class is '
                         'not provided.'))

        super(AppConfigPluginFormMixin, self).__init__(*args, **kwargs)
        # get available event configs, that have the same namespace
        # as pages with namespaces. that will ensure that user wont
        # select config that is not app hooked because that
        # will lead to a 500 error until that config wont be used.
        available_configs = self.config_model.objects.filter(
            namespace__in=Page.objects.exclude(
                application_namespace__isnull=True).values_list(
                'application_namespace', flat=True))

        published_configs_pks = [
            config.pk for config in available_configs
            if namespace_is_apphooked(config.namespace)]

        self.fields['app_config'].queryset = available_configs.filter(
            pk__in=published_configs_pks)
        # inform user that there are not published namespaces
        # which he shouldn't use
        not_published = self.config_model.objects.exclude(
            pk__in=published_configs_pks).values_list(
            'namespace', flat=True)

        # prepare help messages
        msg_not_published = ugettext(
            'Following {0} exists but either pages are not published, or '
            'there is no apphook. To use them - attach them or publish pages '
            'to which they are attached:'.format(self.config_model.__name__))

        not_published_namespaces = '; '.join(not_published)

        additional_message = None
        if not_published.count() > 0:
            # prepare message with list of not published configs.
            additional_message = '{0}\n<br/>{1}'.format(
                msg_not_published, not_published_namespaces)

        # update help text
        if additional_message:
            self.fields['app_config'].help_text += '\n<br/>{0}'.format(
                additional_message)

        # pre select app config if there is only one option
        if self.fields['app_config'].queryset.count() == 1:
                self.fields['app_config'].empty_label = None

    def clean_app_config(self):
        # since namespace is not a unique thing we need to validate it
        # additionally because it is possible that there is a page with same
        # namespace as a jobs config but which is using other app_config, which
        # also would lead to same 500 error. The easiest way is to try to
        # reverse, in case of success that would mean that the app_config is
        # correct and can be used.
        namespace = self.cleaned_data['app_config'].namespace
        if not namespace_is_apphooked(namespace):
            raise ValidationError(
                ugettext(
                    'Seems that selected Job config is not plugged to any '
                    'page, or maybe that page is not published.'
                    'Please select Job config that is being used.'),
                code='invalid')
        return self.cleaned_data['app_config']


class JobListPluginForm(AppConfigPluginFormMixin, forms.ModelForm):
    model = JobListPlugin

    def clean(self):
        data = super(JobListPluginForm, self).clean()
        # save only events for selected app_config
        selected = data.get('jobopenings', [])
        app_config = data.get('app_config')

        new_jobopenings = []
        if app_config is None:
            pass
        else:
            for job in selected:
                if job.category.app_config == app_config:
                    new_jobopenings.append(job)

        data['jobopenings'] = new_jobopenings
        return data


class JobCategoriesListPluginForm(AppConfigPluginFormMixin, forms.ModelForm):
    model = JobCategoriesPlugin

setup_config(JobsConfigForm, JobsConfig)
