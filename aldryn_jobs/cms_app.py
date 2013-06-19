# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from aldryn_jobs.menu import JobCategoryMenu

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


class JobsApp(CMSApp):

    name = _('Jobs')
    urls = ['aldryn_jobs.urls']
    menus = [JobCategoryMenu]

apphook_pool.register(JobsApp)
