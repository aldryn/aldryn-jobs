# -*- coding: utf-8 -*-
from aldryn_jobs.models import JobsConfig
from django.utils.translation import ugettext_lazy as _

from aldryn_apphooks_config.app_base import CMSConfigApp
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from .menu import JobCategoryMenu


class JobsApp(CMSConfigApp):
    name = _('Jobs')
    urls = ['aldryn_jobs.urls']
    menus = [JobCategoryMenu]
    app_config = JobsConfig

apphook_pool.register(JobsApp)
