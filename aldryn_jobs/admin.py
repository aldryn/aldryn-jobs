# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from aldryn_jobs.forms import JobCategoryAdminForm, JobOfferAdminForm
from aldryn_jobs.models import JobApplication, JobCategory, JobOffer

from cms.admin.placeholderadmin import PlaceholderAdmin
from hvad.admin import TranslatableAdmin


class JobApplicationAdmin(admin.ModelAdmin):

    list_display = ['__unicode__', 'created', 'job_offer']
    list_filter = ['job_offer']
    readonly_fields = ['job_offer', 'get_attachment_address']
    fieldsets = [
        (_('Personal infomarion'), {
            'fields': ['first_name', 'last_name', 'email']
        }),
        (_('Cover letter & attachment'), {
            'fields': ['cover_letter', 'get_attachment_address']
        }),
    ]

    def get_attachment_address(self, instance):
        if instance.attachment:
            return mark_safe(u'<a href="%(address)s">%(address)s</a>' % {'address': instance.attachment.url})
        else:
            return u'—'

    get_attachment_address.alow_tags = True
    get_attachment_address.short_description = _('Attachment')


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
                'fields': ['title', 'slug']
            }),
            (_('Options'), {
                'fields': ['category', 'is_active', 'can_apply']
            }),
            (_('Publication period'), {
                'fields': ['publication_start', 'publication_end']
            }),
            # (_('Content'), {
            #     'classes': ['plugin-holder', 'plugin-holder-nopage'],
            #     'fields': ['content']
            # })
        ]
        return fieldsets

admin.site.register(JobApplication, JobApplicationAdmin)
admin.site.register(JobCategory, JobCategoryAdmin)
admin.site.register(JobOffer, JobOfferAdmin)
