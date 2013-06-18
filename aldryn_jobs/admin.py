# -*- coding: utf-8 -*-
from django.contrib import admin

from aldryn_jobs.forms import JobOfferForm
from aldryn_jobs.models import JobCategory, JobOffer

from cms.admin.placeholderadmin import PlaceholderAdmin
from hvad.admin import TranslatableAdmin


class JobCategoryAdmin(TranslatableAdmin):

    list_display = ['__unicode__', 'all_translations']

admin.site.register(JobCategory, JobCategoryAdmin)


class JobOfferAdmin(TranslatableAdmin, PlaceholderAdmin):

    form = JobOfferForm
    list_display = ['__unicode__', 'all_translations']

admin.site.register(JobOffer, JobOfferAdmin)
