# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .forms import (
    NewsletterSignupForm,
    JobListPluginForm,
    JobNewsletterRegistrationPluginForm,
)
from .models import (
    JobListPlugin,
    JobNewsletterRegistrationPlugin,
    JobCategoriesPlugin,
    JobCategoriesListPluginForm,
)
from .utils import namespace_is_apphooked


class NameSpaceCheckMixin(object):

    def render(self, context, instance, placeholder):
        # check if we have a valid app_config that is app hooked to a page.
        # so that we won't have a 500 error if page with that app hook
        # was deleted.
        namespace = (instance.app_config.namespace if instance.app_config
                     else '')

        if not namespace_is_apphooked(namespace):
            context['plugin_configuration_error'] = _(
                'There is an error in plugin configuration: selected Job '
                'config is not available. Please switch to edit mode and '
                'change plugin app_config settings to use valid config. '
                'Also note that aldryn-jobs should be used at least once '
                'as an apphook for that config.')

        return super(NameSpaceCheckMixin, self).render(
            context, instance, placeholder)


class JobCategoriesList(NameSpaceCheckMixin, CMSPluginBase):
    model = JobCategoriesPlugin
    form = JobCategoriesListPluginForm
    module = 'Jobs'
    name = _('Categories list')
    render_template = 'aldryn_jobs/plugins/categories_list.html'


class JobList(NameSpaceCheckMixin, CMSPluginBase):
    form = JobListPluginForm
    model = JobListPlugin
    module = "Jobs"
    name = _('Job List')
    render_template = 'aldryn_jobs/plugins/latest_entries.html'


class JobNewsletter(NameSpaceCheckMixin, CMSPluginBase):
    module = 'Jobs'
    render_template = 'aldryn_jobs/plugins/newsletter_registration.html'
    name = _('Form for Newsletter')
    model = JobNewsletterRegistrationPlugin
    form = JobNewsletterRegistrationPluginForm
    cache = False

    def render(self, context, instance, placeholder):
        context = super(JobNewsletter, self).render(
            context, instance, placeholder)
<<<<<<< HEAD
        # if there is data for form (i.e validation errors) render that form
        # with data. explicitly check that request POST has the right data.
        request = context.get('request')

        # check if we have a valid app_config that is app hooked to a page. so
        # that we won't have a 500 error if page with that app hook was deleted.
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

=======
        # if there is data for form (i.e validation errors) render that
        # form with data. explicitly check that request POST has the right
        # data.
        request = context.get('request')

>>>>>>> Fix issues with plugin app_config field.
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
