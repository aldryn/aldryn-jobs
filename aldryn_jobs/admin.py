# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from django.contrib.sites.models import get_current_site
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from aldryn_apphooks_config.admin import BaseAppHookConfig
from aldryn_reversion.admin import VersionedPlaceholderAdminMixin
from cms import __version__ as cms_version
from cms.admin.placeholderadmin import FrontendEditableAdminMixin
from distutils.version import LooseVersion
from emailit.api import send_mail
from parler.admin import TranslatableAdmin


from .forms import JobCategoryAdminForm, JobOfferAdminForm
from .models import (
    JobApplication, JobCategory, JobOffer,
    JobsConfig, NewsletterSignup
)


def _send_rejection_email(modeladmin, request, queryset, lang_code='',
                          delete_application=False):
    # 1. send rejection email - this should be refactored to use djangos "bulk"
    #    mail
    #
    # Info: Using mass rejection on many JobApplications can lead to a timeout,
    # since SMTPs are not known to be fast

    for application in queryset:
        context = {'job_application': application, }
        send_mail(recipients=[application.email], context=context,
                  template_base='aldryn_jobs/emails/rejection_letter',
                  language=lang_code.lower())

    # 2. update status or delete objects
    qs_count = queryset.count()
    if not delete_application:
        queryset.update(is_rejected=True, rejection_date=now())
        success_msg = _("Successfully sent %(count)s rejection email(s).") % {
            'count': qs_count,
        }
    else:
        queryset.delete()
        success_msg = _("Successfully deleted %(count)s application(s) and "
                        "sent rejection email.") % {'count': qs_count, }

    # 3. inform user with success message
    modeladmin.message_user(request, success_msg)
    return


class SendRejectionEmail(object):
    def __init__(self, lang_code=''):
        super(SendRejectionEmail, self).__init__()
        self.lang_code = lang_code.upper()
        self.name = 'send_rejection_email_{0}'.format(self.lang_code)
        self.title = _("Send rejection e-mail %s" % self.lang_code)

    def __call__(self, modeladmin, request, queryset, *args, **kwargs):
        _send_rejection_email(modeladmin, request, queryset,
                              lang_code=self.lang_code)


class SendRejectionEmailAndDelete(SendRejectionEmail):
    def __init__(self, lang_code=''):
        super(SendRejectionEmailAndDelete, self).__init__(lang_code)
        self.name = 'send_rejection_and_delete_{0}'.format(self.lang_code)
        self.title = _("Send rejection e-mail and delete application %s") % (
            self.lang_code,
        )

    def __call__(self, modeladmin, request, queryset, *args, **kwargs):
        _send_rejection_email(modeladmin, request, queryset,
                              lang_code=self.lang_code, delete_application=True)


class JobApplicationAdmin(VersionedPlaceholderAdminMixin, admin.ModelAdmin):
    list_display = ['__unicode__', 'job_offer', 'created', 'is_rejected',
                    'rejection_date']
    list_filter = ['job_offer', 'is_rejected']
    readonly_fields = ['get_attachment_address']
    raw_id_fields = ['job_offer']

    fieldsets = [
        (_('Job Offer'), {
            'fields': ['job_offer']
        }),
        (_('Personal information'), {
            'fields': ['salutation', 'first_name', 'last_name', 'email']
        }),
        (_('Cover letter & attachments'), {
            'fields': ['cover_letter', 'get_attachment_address']
        })
    ]

    def get_actions(self, request):
        actions = super(JobApplicationAdmin, self).get_actions(request)
        language_codes = [language[0] for language in settings.LANGUAGES]
        for lang_code in language_codes:
            send_rejection_email = SendRejectionEmail(lang_code=lang_code)
            actions[send_rejection_email.name] = (
                send_rejection_email,
                send_rejection_email.name,
                send_rejection_email.title
            )
            send_rejection_and_delete = SendRejectionEmailAndDelete(
                lang_code=lang_code)
            actions[send_rejection_and_delete.name] = (
                send_rejection_and_delete,
                send_rejection_and_delete.name,
                send_rejection_and_delete.title
            )
        return actions

    def has_add_permission(self, request):
        # Don't allow creation of "new" applications via admin-backend until
        # it's properly implemented
        return False

    def get_attachment_address(self, instance):
        attachment_link = '<a href="%(address)s">%(address)s</a>'
        attachments = []

        for attachment in instance.attachments.all():
            if attachment:
                attachments.append(
                    attachment_link % dict(address=attachment.file.url))
        return mark_safe('<br>'.join(attachments)) if attachments else '-'

    get_attachment_address.alow_tags = True
    get_attachment_address.short_description = _('Attachments')


class JobCategoryAdmin(VersionedPlaceholderAdminMixin, TranslatableAdmin):
    form = JobCategoryAdminForm
    list_display = ['__unicode__', 'language_column', 'ordering']
    list_editable = ['ordering']
    filter_horizontal = ['supervisors']

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (_('Translatable fields'), {
                'fields': ['name', 'slug']
            }),
            (_('Supervisors'), {
                'fields': ['supervisors']
            }),
            (_('Options'), {
                'fields': ['app_config']
            })
        ]
        return fieldsets


class JobOfferAdmin(VersionedPlaceholderAdminMixin, FrontendEditableAdminMixin,
                    TranslatableAdmin):
    form = JobOfferAdminForm
    list_display = ['__unicode__', 'language_column']
    frontend_editable_fields = ('title', 'lead_in')
    actions = ['send_newsletter_email']

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (_('Translatable fields'), {
                'fields': ['title', 'slug', 'lead_in']
            }),
            (_('Options'), {
                'fields': ['category', 'is_active', 'can_apply', 'app_config']
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
        # FIXME: this will use admin's domain instead of language specific
        # if site has multiple domains for different languages
        current_domain = get_current_site(request).domain

        job_list = [job.pk for job in queryset]
        sent_emails = NewsletterSignup.objects.send_job_notifiation(
            job_list=job_list, current_domain=current_domain)

        jobs_sent = len(job_list)
        if jobs_sent == 1:
            message_bit = _("1 job was")
        else:
            message_bit = _('%s jobs were') % jobs_sent
        if sent_emails > 0:
            self.message_user(request,
                _('%s successfully sent in the newsletter.') % message_bit)
        else:
            self.message_user(request,
                _('Seems there was some error. Please contact administrator'))
    send_newsletter_email.short_description = _("Send Job Newsletter")


class JobNewsletterSignupAdmin(VersionedPlaceholderAdminMixin,
                               admin.ModelAdmin):
    list_display = ['recipient', 'default_language', 'signup_date',
                    'is_verified', 'is_disabled']
    order_by = ['recipient']


class JobsConfigAdmin(BaseAppHookConfig):
    pass


admin.site.register(JobApplication, JobApplicationAdmin)
admin.site.register(JobCategory, JobCategoryAdmin)
admin.site.register(JobOffer, JobOfferAdmin)
admin.site.register(JobsConfig, JobsConfigAdmin)
admin.site.register(NewsletterSignup, JobNewsletterSignupAdmin)
