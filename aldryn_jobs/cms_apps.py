# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from aldryn_jobs.models import JobsConfig
from aldryn_apphooks_config.app_base import CMSConfigApp
from cms.apphook_pool import apphook_pool


class JobsApp(CMSConfigApp):
    name = _('Jobs')
    app_config = JobsConfig
    urls = ['aldryn_jobs.urls']  # COMPAT: CMS3.2

    def get_urls(self, *args, **kwargs):
        return self.urls


apphook_pool.register(JobsApp)
