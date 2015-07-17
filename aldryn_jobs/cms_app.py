# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from aldryn_jobs.models import JobsConfig
from aldryn_apphooks_config.app_base import CMSConfigApp
from cms.apphook_pool import apphook_pool


class JobsApp(CMSConfigApp):
    name = _('Jobs')
    urls = ['aldryn_jobs.urls']
    app_config = JobsConfig

apphook_pool.register(JobsApp)
