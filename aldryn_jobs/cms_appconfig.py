# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from aldryn_apphooks_config.models import AppHookConfig
from cms.models.fields import PlaceholderField
from parler.models import TranslatableModel, TranslatedFields


class JobsConfig(TranslatableModel, AppHookConfig):
    # Job PHFs
    placeholder_jobs_top = PlaceholderField(
        'jobs_top', related_name='aldryn_jobs_top')

    placeholder_jobs_sidebar = PlaceholderField(
        'jobs_sidebar', related_name='aldryn_jobs_sidebar')

    # Job detail PHFs
    placeholder_jobs_detail_top = PlaceholderField(
        'jobs_detail_top', related_name='aldryn_jobs_detail_top')

    placeholder_jobs_detail_bottom = PlaceholderField(
        'jobs_detail_bottom', related_name='aldryn_jobs_detail_bottom')

    placeholder_jobs_detail_footer = PlaceholderField(
        'jobs_detail_footer', related_name='aldryn_jobs_detail_footer')

    # Jobs list PHFs
    placeholder_jobs_list_top = PlaceholderField(
        'jobs_list_top', related_name='aldryn_jobs_list_top')

    placeholder_jobs_list_bottom = PlaceholderField(
        'jobs_list_bottom', related_name='aldryn_jobs_list_bottom')

    # Jobs plugins PHFs
    placeholder_jobs_newsletter_registration = PlaceholderField(
        'jobs_newsletter_registration',
        related_name='aldryn_jobs_newsletter_registration')
