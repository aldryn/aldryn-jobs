# -*- coding: utf-8 -*-
from django import forms
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, get_language

from aldryn_jobs.models import JobApplication

from emailit.api import send_mail
from hvad.forms import TranslatableModelForm
from unidecode import unidecode


class AutoSlugForm(TranslatableModelForm):

    slug_field = 'slug'
    slugified_field = None

    def clean(self):
        super(AutoSlugForm, self).clean()
        if self.slug_field not in self.data:
            slug = self.generate_slug()
            # add to self.data in order to show generated slug in the form in case of an error
            self.data[self.slug_field] = self.cleaned_data[self.slug_field] = slug
        else:
            slug = self.cleaned_data[self.slug_field]

        # validate uniqueness
        conflict = self.get_slug_conflict(slug=slug)
        if conflict:
            self.report_error(conflict=conflict)

        return self.cleaned_data

    def generate_slug(self):
        return slugify(unidecode(self.cleaned_data[self.slugified_field]))

    def get_slug_conflict(self, slug):
        translations_model = self.instance._meta.translations_model

        try:
            language_code = self.instance.language_code
        except translations_model.DoesNotExist:
            language_code = get_language()

        qs = translations_model.objects.filter(slug=slug, language_code=language_code)
        if self.instance.pk:
            qs = qs.exclude(master=self.instance)

        try:
            return qs.get()
        except translations_model.DoesNotExist:
            return None

    def report_error(self, conflict):
        address = '<a href="%(url)s">%(label)s</a>' % {
            'url': conflict.master.get_absolute_url(),
            'label': ugettext('the conflicting object')}
        error_message = ugettext('Conflicting slug. See %(address)s.') % {'address': address}
        self.append_to_errors(field='slug', message=mark_safe(error_message))

    def append_to_errors(self, field, message):
        try:
            self._errors[field].append(message)
        except KeyError:
            self._errors[field] = self.error_class([message])


class JobCategoryAdminForm(AutoSlugForm):

    slugified_field = 'name'

    class Meta:
        fields = ['name', 'slug', 'supervisors']


class JobOfferAdminForm(AutoSlugForm):

    slugified_field = 'title'


class JobApplicationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.job_offer = kwargs.pop('job_offer')
        super(JobApplicationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = JobApplication
        fields = ['first_name', 'last_name', 'email', 'cover_letter', 'attachment']

    def save(self, commit=True):
        super(JobApplicationForm, self).save(commit=False)
        self.instance.job_offer = self.job_offer
        if commit:
            self.instance.save()

        # additional actions while applying for the job
        self.send_confirmation_email()
        self.send_staff_notifications()

        return self.instance

    def send_confirmation_email(self):
        context = {'job_application': self.instance}
        send_mail(recipients=[self.instance.email], context=context, template_base='aldryn_jobs/emails/confirmation')

    def send_staff_notifications(self):
        recipients = self.instance.job_offer.get_notification_emails()
        context = {'job_application': self.instance}
        send_mail(recipients=recipients, context=context, template_base='aldryn_jobs/emails/notification')
