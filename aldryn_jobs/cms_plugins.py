# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from aldryn_jobs import models


class JobList(CMSPluginBase):
    module = "Jobs"
    render_template = 'aldryn_jobs/plugins/job_list.html'
    name = _('Job List')
    model = models.JobListPlugin

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        return context


plugin_pool.register_plugin(JobList)
