# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

from django import forms, get_version
from django.conf import settings
from django.core.exceptions import (
    NON_FIELD_ERRORS,
    ObjectDoesNotExist,
    ValidationError,
)
from django.core.urlresolvers import reverse, NoReverseMatch
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.translation import pgettext_lazy as _, get_language

from aldryn_apphooks_config.utils import setup_config
from app_data import AppDataForm
from cms import __version__ as cms_version
from cms.models import Page
from distutils.version import LooseVersion, StrictVersion
from emailit.api import send_mail
from multiupload.fields import MultiFileField
from parler.forms import TranslatableModelForm
from unidecode import unidecode


from .models import (
    JobApplication, JobApplicationAttachment, JobCategory, JobOffer,
    NewsletterSignup, JobsConfig,
    JobListPlugin, JobNewsletterRegistrationPlugin)


SEND_ATTACHMENTS_WITH_EMAIL = getattr(settings, 'ALDRYN_JOBS_SEND_ATTACHMENTS_WITH_EMAIL', True)
DEFAULT_SEND_TO = getattr(settings, 'ALDRYN_JOBS_DEFAULT_SEND_TO', None)


class AutoSlugForm(TranslatableModelForm):

    slug_field = 'slug'
    slugified_field = None

    def __init__(self, *args, **kwargs):
        super(AutoSlugForm, self).__init__(*args, **kwargs)
        if 'app_config' in self.fields:
            # if has only one choice, select it by default
            if self.fields['app_config'].queryset.count() == 1:
                self.fields['app_config'].empty_label = None

    def clean(self):
        super(AutoSlugForm, self).clean()

        if not self.data.get(self.slug_field):
            slug = self.generate_slug()
            raw_data = self.data.copy()
            # add to self.data in order to show generated slug in the
            # form in case of an error
            raw_data[self.slug_field] = self.cleaned_data[self.slug_field] = slug

            # We cannot modify self.data directly because it can be
            # Immutable QueryDict
            self.data = raw_data
        else:
            slug = self.cleaned_data[self.slug_field]

        # validate uniqueness
        conflict = self.get_slug_conflict(slug=slug)
        if conflict:
            self.report_error(conflict=conflict)

        return self.cleaned_data

    def generate_slug(self):
        content_to_slugify = self.cleaned_data.get(self.slugified_field, '')
        return slugify(unidecode(content_to_slugify))

    def get_slug_conflict(self, slug):
        try:
            language_code = self.instance.get_current_language()
        except ObjectDoesNotExist:
            language_code = get_language()

        conflicts = (
            self._meta.model.objects.language(language_code).translated(
                language_code, slug=slug)
        )
        if self.is_edit_action():
            conflicts = conflicts.exclude(pk=self.instance.pk)

        try:
            return conflicts.get()
        except self._meta.model.DoesNotExist:
            return None

    def report_error(self, conflict):
        address = '<a href="%(url)s" target="_blank">%(label)s</a>' % {
            'url': conflict.master.get_absolute_url(),
            'label': _('aldryn-jobs', 'the conflicting object')}
        error_message = (
            _('aldryn-jobs', 'Conflicting slug. See %(address)s.') % {
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


class JobCategoryAdminForm(AutoSlugForm):

    slugified_field = 'name'

    class Meta:
        model = JobCategory
        fields = ['name', 'slug', 'supervisors', 'app_config']


class JobOfferAdminForm(AutoSlugForm):

    slugified_field = 'title'

    class Meta:
        model = JobOffer
        fields = [
            'title',
            'slug',
            'lead_in',
            'category',
            'is_active',
            'can_apply',
            'app_config',
            'publication_start',
            'publication_end'
        ]

        if LooseVersion(cms_version) < LooseVersion('3.0'):
            fields.append('content')

    def __init__(self, *args, **kwargs):
        super(JobOfferAdminForm, self).__init__(*args, **kwargs)

        # small monkey patch to show better label for categories
        def label_from_instance(obj):
            return "{0} / {1}".format(obj.app_config, obj)
        self.fields['category'].label_from_instance = label_from_instance

    def clean(self):
        cleaned_data = super(JobOfferAdminForm, self).clean()
        category = cleaned_data.get('category')
        app_config = cleaned_data.get('app_config')
        if category and category.app_config != app_config:
            self.append_to_errors(
                'category',
                _('aldryn-jobs', 'Category app_config must be the same '
                                 'selected for Job Offer')
            )
        return cleaned_data


class JobApplicationForm(forms.ModelForm):
    attachments = MultiFileField(
        max_num=getattr(settings, 'ALDRYN_JOBS_ATTACHMENTS_MAX_COUNT', 5),
        min_num=getattr(settings, 'ALDRYN_JOBS_ATTACHMENTS_MIN_COUNT', 0),
        max_file_size=getattr(settings,
            'ALDRYN_JOBS_ATTACHMENTS_MAX_FILE_SIZE', 1024 * 1024 * 5),
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.job_offer = kwargs.pop('job_offer')
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
        self.instance.job_offer = self.job_offer

        if commit:
            self.instance.save()

        for each in self.cleaned_data['attachments']:
            att = JobApplicationAttachment(application=self.instance, file=each)
            att.save()

        # additional actions while applying for the job
        self.send_confirmation_email()
        self.send_staff_notifications()

        return self.instance

    def send_confirmation_email(self):
        context = {'job_application': self.instance}
        send_mail(recipients=[self.instance.email],
                  context=context,
                  template_base='aldryn_jobs/emails/confirmation')

    def send_staff_notifications(self):
        recipients = self.instance.job_offer.get_notification_emails()
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


class NewsletterSignupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.app_config = kwargs.pop('app_config')
        super(NewsletterSignupForm, self).__init__(*args, **kwargs)

    def clean(self):

        obj_qs = NewsletterSignup.objects.filter(
            recipient=self.data['recipient'],
            app_config=self.app_config)
        if obj_qs.count() > 0:
            # TODO: Handle multiple objects! rasie or handle them properly
            raise ValidationError(
                _('aldryn-jobs',
                  "This email is already registered."),
                code='invalid')
        return super(NewsletterSignupForm, self).clean()

    class Meta:
        model = NewsletterSignup
        fields = ['recipient']
        labels = {
            'recipient': _('aldryn-jobs', 'Email'),
        }


class NewsletterConfirmationForm(forms.ModelForm):

    class Meta:
        model = NewsletterSignup
        fields = ['confirmation_key']
        widgets = {
            'confirmation_key': forms.HiddenInput(),
        }


class NewsletterUnsubscriptionForm(NewsletterConfirmationForm):
    # form is actually the same
    # if it shouldn't be the same - please rewrite this form
    pass


class NewsletterResendConfirmationForm(NewsletterConfirmationForm):
    # form is actually the same, but for confirming the resend action
    # if it shouldn't be the same - please rewrite this form
    pass


class JobsConfigForm(AppDataForm):
    pass


class JobListPluginForm(forms.ModelForm):
    model = JobListPlugin

    def add_error(self, field, error):
        # TODO: move it to a form mixin in aldryn-commons would be good idea?
        #       (or even something more generic)
        if StrictVersion(get_version()) >= StrictVersion('1.7'):
            return super(JobListPluginForm, self).add_error(field, error)

        if not isinstance(error, ValidationError):
            # Normalize to ValidationError and let its constructor
            # do the hard work of making sense of the input.
            error = ValidationError(error)

        if hasattr(error, 'error_dict'):
            if field is not None:
                raise TypeError(
                    "The argument `field` must be `None` when the `error` "
                    "argument contains errors for multiple fields."
                )
            else:
                error = error.error_dict
        else:
            error = {field or NON_FIELD_ERRORS: error}
        for field, error_list in error.items():
            if field not in self.errors:
                if field != NON_FIELD_ERRORS and field not in self.fields:
                    raise ValueError("'%s' has no field named '%s'." % (
                        self.__class__.__name__, field))
                self._errors[field] = self.error_class()
            self._errors[field].extend(error_list.messages)
            if field in self.cleaned_data:
                del self.cleaned_data[field]

    def clean(self):
        data = super(JobListPluginForm, self).clean()
        app_config = data.get('app_config')
        offers = data.get('joboffers')
        if app_config and offers:
            for offer in offers:
                if offer.app_config != app_config:
                    self.add_error(
                        'joboffers',
                        _('aldryn-jobs',
                          "Job Offer '%(joboffer)s' does not match app_config "
                          "'%(config)s'. Please, remove it from selected Job "
                          "Offers.") % {'joboffer': offer,
                                        'config': app_config}
                    )
                    if 'joboffers' in data:
                        data.pop('joboffers')
        return data


class JobNewsletterRegistrationPluginForm(forms.ModelForm):
    model = JobNewsletterRegistrationPlugin

    def __init__(self, *args, **kwargs):
        super(JobNewsletterRegistrationPluginForm, self).__init__(
            *args, **kwargs)
        # get available jobs configs, that have the same namespace as
        # pages with namespaces. That will ensure that user wont select
        # config that is not app hooked because that will lead to a 500
        # error until that config wont be used.
        available_configs = JobsConfig.objects.filter(
            namespace__in=Page.objects.exclude(
                application_namespace__isnull=True).values_list(
                'application_namespace', flat=True))
        self.fields['app_config'].queryset = available_configs

    def clean(self):
        # since namespace is not a unique thing we need to validate it
        # additionally because it is possible that there is a page with same
        # namespace as a jobs config but which is using other app_config,
        # which also would lead to same 500 error. The easiest way is to try
        # to reverse, in case of success that would mean that the app_config
        # is correct and can be used.
        data = super(JobNewsletterRegistrationPluginForm, self).clean()
        try:
            reverse('{0}:register_newsletter'.format(
                data['app_config'].namespace))
        except NoReverseMatch:
            raise ValidationError(
                _('aldryn-jobs',
                  'Seems that selected Job config is not plugged to any page, '
                  'or maybe that page is not published.'
                  'Please select Job config that is being used.'),
                code='invalid')
        return data


setup_config(JobsConfigForm, JobsConfig)
