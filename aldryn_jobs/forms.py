# -*- coding: utf-8 -*-
import os
import cms

from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _, get_language

from multiupload.fields import MultiFileField
from distutils.version import LooseVersion
from emailit.api import send_mail
from parler.forms import TranslatableModelForm
from unidecode import unidecode

from .models import (
    JobApplication, JobApplicationAttachment, JobCategory, JobOffer, NewsletterSignup
)


SEND_ATTACHMENTS_WITH_EMAIL = getattr(settings, 'ALDRYN_JOBS_SEND_ATTACHMENTS_WITH_EMAIL', True)


class AutoSlugForm(TranslatableModelForm):

    slug_field = 'slug'
    slugified_field = None

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
            self._meta.model.objects.language(language_code)
                              .translated(language_code, slug=slug)
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
            'label': _('the conflicting object')}
        error_message = (
            _('Conflicting slug. See %(address)s.') % {'address': address}
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
        fields = ['name', 'slug', 'supervisors']


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
            'publication_start',
            'publication_end'
        ]

        if LooseVersion(cms.__version__) < LooseVersion('3.0'):
            fields.append('content')


class JobApplicationForm(forms.ModelForm):
    attachments  = MultiFileField(
        max_num=getattr(settings, 'ALDRYN_JOBS_ATTACHMENTS_MAX_COUNT', 5),
        min_num=getattr(settings, 'ALDRYN_JOBS_ATTACHMENTS_MIN_COUNT', 0),
        max_file_size=getattr(settings, 'ALDRYN_JOBS_ATTACHMENTS_MAX_FILE_SIZE', 1024*1024*5),
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
            context['admin_change_form_url'] = self.request.build_absolute_uri(admin_change_form)

        kwargs = {}
        if SEND_ATTACHMENTS_WITH_EMAIL:
            attachments = self.instance.attachments.all()
            if attachments:
                kwargs['attachments'] = []
                for attachment in attachments:
                    attachment.file.seek(0)
                    kwargs['attachments'].append(
                        (os.path.split(attachment.file.name)[1], attachment.file.read(),))
        send_mail(recipients=recipients,
                  context=context,
                  template_base='aldryn_jobs/emails/notification', **kwargs)


class NewsletterSignupForm(forms.ModelForm):

    class Meta:
        model = NewsletterSignup
        fields = ['recipient']
        labels = {
            'recipient': _('Email'),
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
