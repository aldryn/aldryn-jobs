# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .forms import (
    JobListPluginForm,
    JobCategoriesListPluginForm,
)
from .models import (
    JobListPlugin,
    JobCategoriesPlugin,
    JobOpening,
)
from .utils import namespace_is_apphooked


class NameSpaceCheckMixin(object):

    def render(self, context, instance, placeholder):
        # check if we have a valid app_config that is app hooked to a page.
        # so that we won't have a 500 error if page with that app hook
        # was deleted.
        if instance.app_config:
            namespace = instance.app_config.namespace
        else:
            namespace = ''

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

    def render(self, context, instance, placeholder):
        context = super(JobList, self).render(context, instance, placeholder)
        if instance.app_config:
            namespace = instance.app_config.namespace
        else:
            namespace = ''
        if namespace == '' or context.get('plugin_configuration_error', False):
            vacancies = JobOpening.objects.none()
        else:
            vacancies = instance.get_job_openings(namespace)
        context['vacancies'] = vacancies
        context['vacancies_count'] = len(vacancies)
        return context


plugin_pool.register_plugin(JobCategoriesList)
plugin_pool.register_plugin(JobList)
