# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import (
    JobListPlugin, JobNewsletterRegistrationPlugin, JobCategoriesPlugin,
    JobsConfig)
from .forms import NewsletterSignupForm, JobListPluginForm, JobNewsletterRegistrationPluginForm


class JobCategoriesList(CMSPluginBase):
    model = JobCategoriesPlugin
    module = 'Jobs'
    name = _('Categories list')
    render_template = 'aldryn_jobs/plugins/categories_list.html'


class JobList(CMSPluginBase):
    form = JobListPluginForm
    model = JobListPlugin
    module = "Jobs"
    name = _('Job List')
    render_template = 'aldryn_jobs/plugins/latest_entries.html'


class JobNewsletter(CMSPluginBase):
    module = 'Jobs'
    render_template = 'aldryn_jobs/plugins/newsletter_registration.html'
    name = _('Form for Newsletter')
    model = JobNewsletterRegistrationPlugin
    form = JobNewsletterRegistrationPluginForm
    cache = False

    def render(self, context, instance, placeholder):
        context = super(JobNewsletter, self).render(context, instance, placeholder)
        # if there is data for form (i.e validation errors) render that
        # form with data. explicitly check that request POST has the right
        # data.
        request = context.get('request')

        # check if we have a valid app_config that is app hooked to a page.
        # so that we won't have a 500 error if page with that app hook
        # was deleted.
        try:
            reverse('{0}:register_newsletter'.format(
                instance.app_config.namespace))
        except (NoReverseMatch, AttributeError):
            context['plugin_configuration_error'] = _(
                'There is an error in plugin configuration: selected job '
                'config is not available. Please switch to edit mode and '
                'change plugin app_config settings to use valid config. '
                'Also note that aldryn-jobs should be used at least once as an '
                'apphook for that config.')

        if request is not None and request.POST.get('recipient'):
            context['form'] = NewsletterSignupForm(
                request.POST, app_config=instance.app_config)
        else:
            context['form'] = NewsletterSignupForm(
                app_config=instance.app_config)
        return context


plugin_pool.register_plugin(JobCategoriesList)
plugin_pool.register_plugin(JobList)
plugin_pool.register_plugin(JobNewsletter)
