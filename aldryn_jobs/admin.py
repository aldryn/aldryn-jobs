# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from adminsortable2.admin import SortableAdminMixin
from aldryn_apphooks_config.admin import BaseAppHookConfig
from aldryn_reversion.admin import VersionedPlaceholderAdminMixin
from aldryn_translation_tools.admin import (
    AllTranslationsMixin,
    LinkedRelatedInlineMixin,
)
from cms import __version__ as cms_version
from cms.admin.placeholderadmin import FrontendEditableAdminMixin
from distutils.version import LooseVersion
from emailit.api import send_mail
from parler.admin import TranslatableAdmin


from .forms import JobCategoryAdminForm, JobOpeningAdminForm
from .models import JobApplication, JobCategory, JobOpening, JobsConfig


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
        success_msg = _("Successfully sent {0} rejection email(s).").format(
            qs_count)
    else:
        queryset.delete()
        success_msg = _("Successfully deleted {0} application(s) and sent "
                        "rejection email.").format(qs_count)

    # 3. inform user with success message
    modeladmin.message_user(request, success_msg)
    return


class SendRejectionEmail(object):
    def __init__(self, lang_code=''):
        super(SendRejectionEmail, self).__init__()
        self.lang_code = lang_code.upper()
        self.name = 'send_rejection_email_{0}'.format(self.lang_code)
        self.title = _("Send rejection e-mail {0}").format(self.lang_code)

    def __call__(self, modeladmin, request, queryset, *args, **kwargs):
        _send_rejection_email(modeladmin, request, queryset,
                              lang_code=self.lang_code)


class SendRejectionEmailAndDelete(SendRejectionEmail):
    def __init__(self, lang_code=''):
        super(SendRejectionEmailAndDelete, self).__init__(lang_code)
        self.name = 'send_rejection_and_delete_{0}'.format(self.lang_code)
        self.title = _("Send rejection e-mail and delete "
                       "application {0}").format(self.lang_code)

    def __call__(self, modeladmin, request, queryset, *args, **kwargs):
        _send_rejection_email(modeladmin, request, queryset,
                              lang_code=self.lang_code, delete_application=True)


class JobApplicationAdmin(VersionedPlaceholderAdminMixin, admin.ModelAdmin):
    list_display = ['__str__', 'job_opening', 'created', 'is_rejected',
                    'rejection_date', ]
    list_filter = ['job_opening', 'is_rejected']
    readonly_fields = ['get_attachment_address']
    raw_id_fields = ['job_opening']

    fieldsets = [
        (_('Job Opening'), {
            'fields': ['job_opening']
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
        attachment_link = '<a href="{address}">{address}</a>'
        attachments = []

        for attachment in instance.attachments.all():
            if attachment:
                attachments.append(
                    attachment_link.format(address=attachment.file.url))
        return mark_safe('<br>'.join(attachments)) if attachments else '-'

    get_attachment_address.allow_tags = True
    get_attachment_address.short_description = _('Attachments')


class JobCategoryAdmin(VersionedPlaceholderAdminMixin,
                       SortableAdminMixin, AllTranslationsMixin,
                       TranslatableAdmin):
    form = JobCategoryAdminForm
    list_display = ['__str__', 'app_config']
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


class JobApplicationInline(LinkedRelatedInlineMixin, admin.TabularInline):
    model = JobApplication
    fields = ['email', 'is_rejected', ]
    readonly_fields = ['email', 'is_rejected', ]

    def has_add_permission(self, request):
        return False


class JobOpeningAdmin(VersionedPlaceholderAdminMixin,
                      AllTranslationsMixin,
                      SortableAdminMixin,
                      FrontendEditableAdminMixin,
                      TranslatableAdmin):
    form = JobOpeningAdminForm
    list_display = ['__str__', 'category', 'num_applications', ]
    frontend_editable_fields = ('title', 'lead_in')
    inlines = [JobApplicationInline, ]

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

        if LooseVersion(cms_version) < LooseVersion('3.0'):
            content_fieldset = {
                'classes': ['plugin-holder', 'plugin-holder-nopage'],
                'fields': ['content']
            }
            fieldsets.append((_('Content'), content_fieldset))
        return fieldsets

    def get_queryset(self, request):
        qs = super(JobOpeningAdmin, self).queryset(request)
        qs = qs.annotate(applications_count=models.Count('applications'))
        return qs

    def num_applications(self, obj):
        return obj.applications_count
    num_applications.short_description = '# Applications'
    num_applications.admin_order_field = 'applications_count'


class JobsConfigAdmin(VersionedPlaceholderAdminMixin, BaseAppHookConfig):
    pass


admin.site.register(JobApplication, JobApplicationAdmin)
admin.site.register(JobCategory, JobCategoryAdmin)
admin.site.register(JobOpening, JobOpeningAdmin)
admin.site.register(JobsConfig, JobsConfigAdmin)
