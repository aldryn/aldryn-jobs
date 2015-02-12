# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from aldryn_jobs import models
from .forms import NewsletterSignupForm


class JobList(CMSPluginBase):
    module = "Jobs"
    render_template = 'aldryn_jobs/plugins/latest_entries.html'
    name = _('Job List')
    model = models.JobListPlugin

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        return context


class JobNewsletter(CMSPluginBase):
    module = 'Jobs'
    render_template = 'aldryn_jobs/plugins/newsletter_registration.html'
    name = _('Form for Newsletter')
    model = models.JobNewsletterRegistrationPlugin

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        # if there is data for form (i.e validation errors) render that form with data.
        # explicitly check that request POST has the right data.
        request = context.get('request')
        if request is not None and request.POST.get('recipient'):
            context['form'] = NewsletterSignupForm(request.POST)
        else:
            context['form'] = NewsletterSignupForm()
        return context


plugin_pool.register_plugin(JobList)
plugin_pool.register_plugin(JobNewsletter)