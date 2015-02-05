# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.contrib.sites.models import get_current_site
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.timezone import now

import cms
from cms.utils.i18n import force_language
from cms.admin.placeholderadmin import PlaceholderAdmin
from cms.admin.placeholderadmin import FrontendEditableAdmin
from distutils.version import LooseVersion
from emailit.api import send_mail
from hvad.admin import TranslatableAdmin

from .forms import JobCategoryAdminForm, JobOfferAdminForm
from .models import (JobApplication, JobCategory, JobOffer, JobApplicationAttachment,
    NewsletterSignup)


def _send_rejection_email(modeladmin, request, queryset, delete_application=False):
    # 1. send rejection email - this should be refactored to use djangos "bulk" mail
    #
    # Info: Using mass rejection on many JobApplications can lead to a timeout, since SMTPs are not known to be fast

    for application in queryset:
        context = {'job_application': application, }
        send_mail(recipients=[application.email], context=context, template_base='aldryn_jobs/emails/rejection_letter')

    # 2. update status or delete objects
    qs_count = queryset.count()
    if not delete_application:
        queryset.update(is_rejected=True, rejection_date=now())
        success_msg = _("Successfully sent %(count)s rejection email(s).") % {'count': qs_count, }
    else:
        queryset.delete()
        success_msg = _("Successfully deleted %(count)s application(s) and sent rejection email.") % { 'count': qs_count, }

    # 3. inform user with success message
    modeladmin.message_user(request, success_msg)
    return


def send_rejection_email(modeladmin, request, queryset):
    _send_rejection_email(modeladmin, request, queryset)


send_rejection_email.short_description = _("Send rejection e-mail")


def send_rejection_and_delete(modeladmin, request, queryset):
    _send_rejection_email(modeladmin, request, queryset, delete_application=True)


send_rejection_and_delete.short_description = _("Send rejection e-mail and delete application")


class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'job_offer', 'created', 'is_rejected', 'rejection_date']
    list_filter = ['job_offer', 'is_rejected']
    readonly_fields = ['job_offer', 'get_attachment_address']
    actions = [send_rejection_email, send_rejection_and_delete]

    fieldsets = [
        (_('Personal information'), {
            'fields': ['salutation', 'first_name', 'last_name', 'email']
        }),
        (_('Cover letter & attachments'), {
            'fields': ['cover_letter', 'get_attachment_address']
        }),
    ]

    def has_add_permission(self, request):
        # Don't allow creation of "new" applications via admin-backend until it's properly implemented
        return False

    def get_attachment_address(self, instance):
        attachment_link = u'<a href="%(address)s">%(address)s</a>'
        attachments = []

        for attachment in instance.attachments.all():
            if attachment:
                attachments.append(attachment_link % dict(address=attachment.file.url))
        return mark_safe('<br>'.join(attachments)) if attachments else u'-'

    get_attachment_address.alow_tags = True
    get_attachment_address.short_description = _('Attachments')


class JobCategoryAdmin(TranslatableAdmin):
    form = JobCategoryAdminForm
    list_display = ['__unicode__', 'all_translations', 'ordering']
    list_editable = ['ordering']
    filter_horizontal = ['supervisors']

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (_('Translatable fields'), {
                'fields': ['name', 'slug']
            }),
            (_('Supervisors'), {
                'fields': ['supervisors']
            })
        ]
        return fieldsets


class JobOfferAdmin(FrontendEditableAdmin, TranslatableAdmin, PlaceholderAdmin):
    form = JobOfferAdminForm
    list_display = ['__unicode__', 'all_translations']
    frontend_editable_fields = ('title', 'lead_in')
    actions = ['send_newsletter_email']
    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (_('Translatable fields'), {
                'fields': ['title', 'slug', 'lead_in']
            }),
            (_('Options'), {
                'fields': ['category', 'is_active', 'can_apply']
            }),
            (_('Publication period'), {
                'fields': ['publication_start', 'publication_end']
            })
        ]

        if LooseVersion(cms.__version__) < LooseVersion('3.0'):
            content_fieldset = {
                'classes': ['plugin-holder', 'plugin-holder-nopage'],
                'fields': ['content']
            }
            fieldsets.append((_('Content'), content_fieldset))
        return fieldsets

    def send_newsletter_email(self, request, queryset):
        """
        Sends a newsletter to all active recipients.
        """
        recipients = NewsletterSignup.objects.active_recipients()
        # TODO: get from settings if we need to send all translations or
        # translations for recipient.default_language (NewsletterSignup) only
        # FIXME: this will use admin's domain instead of language specific
        current_domain = get_current_site(request).domain
        # build links for jobs for all translations
        jobs = []
        for job in queryset:
            for job_translation in job.translations.all():
                jobs.append({
                    'job': job_translation,
                    'link': '{0}{1}'.format(current_domain,
                                            job.get_absolute_url(
                                                language=job_translation.language_code))
                })

        for recipient_user in recipients:
            kwargs = {'key': recipient_user.confirmation_key}
            link = reverse('unsubscribe_from_newsletter', kwargs=kwargs)
            unsubscribe_link = '{0}{1}'.format(current_domain, link)
            context = {
                'jobs': jobs,
                'unsubscribe_link': unsubscribe_link,
            }

            with force_language(recipient_user.default_language):
                send_mail(recipients=[recipient_user.recipient],
                          context=context,
                          template_base='aldryn_jobs/emails/newsletter_job_offers')
        jobs_sent = len(jobs)
        if jobs_sent == 1:
            message_bit = _("1 job was")
        else:
            message_bit = "%s jobs were" % jobs_sent
        self.message_user(request, "%s successfully sent in the newsletter." % message_bit)
    send_newsletter_email.short_description = _("Send Job Newsletter")

class JobNewsletterSignupAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'default_language', 'signup_date', 'is_verified', 'is_disabled']

admin.site.register(JobApplication, JobApplicationAdmin)
admin.site.register(JobCategory, JobCategoryAdmin)
admin.site.register(JobOffer, JobOfferAdmin)
admin.site.register(NewsletterSignup, JobNewsletterSignupAdmin)