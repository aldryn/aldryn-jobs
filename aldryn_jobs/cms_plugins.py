# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import JobListPlugin


class JobList(CMSPluginBase):
    module = "Jobs"
    render_template = 'aldryn_jobs/plugins/latest_entries.html'
    name = _('Job List')
    model = JobListPlugin

    def render(self, context, instance, placeholder):
        import ipdb;ipdb.set_trace()
        context['instance'] = instance
        return context


plugin_pool.register_plugin(JobList)
