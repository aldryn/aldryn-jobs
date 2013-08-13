# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from aldryn_jobs.forms import JobCategoryAdminForm, JobOfferAdminForm
from aldryn_jobs.models import JobApplication, JobCategory, JobOffer

import cms
from cms.admin.placeholderadmin import PlaceholderAdmin
from hvad.admin import TranslatableAdmin
from distutils.version import LooseVersion


class JobApplicationAdmin(admin.ModelAdmin):

    list_display = ['__unicode__', 'created', 'job_offer']
    list_filter = ['job_offer']
    readonly_fields = ['job_offer', 'get_attachment_address']
    fieldsets = [
        (_('Personal information'), {
            'fields': ['salutation', 'first_name', 'last_name', 'email']
        }),
        (_('Cover letter & attachments'), {
            'fields': ['cover_letter', 'get_attachment_address']
        }),
    ]

    def get_attachment_address(self, instance):
        attachment_fields = ['attachment', 'attachment_2', 'attachment_3', 'attachment_4']
        attachment_link = u'<a href="%(address)s">%(address)s</a>'
        attachments = []

        for field in attachment_fields:
            attachment = getattr(instance, field, None)
            if attachment:
                attachments.append(attachment_link % dict(address=attachment.url))
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


class JobOfferAdmin(TranslatableAdmin, PlaceholderAdmin):

    form = JobOfferAdminForm
    list_display = ['__unicode__', 'all_translations']

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

admin.site.register(JobApplication, JobApplicationAdmin)
admin.site.register(JobCategory, JobCategoryAdmin)
admin.site.register(JobOffer, JobOfferAdmin)
