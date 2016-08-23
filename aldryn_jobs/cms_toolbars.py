# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import resolve, Resolver404
from django.utils.translation import (
    ugettext_lazy as _,
    get_language_from_request
)

from aldryn_apphooks_config.utils import get_app_instance
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.utils.urlutils import admin_reverse

from .cms_appconfig import JobsConfig
from .models import JobOpening


def get_jobopening_from_path(path, language, current_url=None):
    # There is an issue with resolve(path) which is related to django cache
    # (django functools memoize) which uses usual dict and cannot be disabled
    # that leads to a Resolver404 because that cache contains wrong language
    # url resolver. Since request at the moment of calling this function
    # already contains resolver with desired result - we will try to use that
    # In best case this block of code (current_url is None) won't be
    # executed, but if it is - we'll try to get this resolved or will fail
    # with pointing to this place and catch traceback, THE REAL one.
    if current_url is None:
        try:
            current_url = resolve(path)
        except Resolver404:
            raise ImproperlyConfigured(
                "Could not resolve path to obtain current url for"
                " populating cms menu")

    if current_url.url_name == 'job-opening-detail':
        # since identical names are allowed with different namespaces -
        # perform correct lookup.
        job_opening = JobOpening.objects.language(
            language).namespace(current_url.namespace)

        if 'category_slug' in current_url.kwargs:
            category_slug = current_url.kwargs['category_slug']
            job_opening = job_opening.filter(
                category__translations__slug=category_slug,
                category__translations__language_code=language
            )

        if 'job_opening_slug' in current_url.kwargs:
            job_slug = current_url.kwargs['job_opening_slug']
            job_opening = job_opening.translated(language, slug=job_slug)

        if job_opening.count():
            # Let MultipleObjectsReturned propagate if it is raised
            return job_opening.get()

    return None


@toolbar_pool.register
class JobsToolbar(CMSToolbar):

    def get_jobs_config(self):
        try:
            __, config = get_app_instance(self.request)
            if not isinstance(config, JobsConfig):
                # This is not the app_hook you are looking for.
                return None
        except ImproperlyConfigured:
            # There is no app_hook at all.
            return None

        return config

    def populate(self):
        def can(actions, model):
            try:
                # Py2
                basestring = basestring
            except NameError:
                # Py3
                basestring = (str, bytes)

            if isinstance(actions, basestring):
                actions = [actions]
            for action in actions:
                perm = 'aldryn_jobs.%(action)s_%(model)s' % {
                    'action': action, 'model': model
                }
                if not self.request.user.has_perm(perm):
                    return False
            return True

        if self.is_current_app and (can(['add', 'change'], 'jobopening') or
                                    can(['add', 'change'], 'jobsconfig')):
            menu = self.toolbar.get_or_create_menu('jobs-app', _('Jobs'))

            # try to reuse resolver_match instead of doing double work with
            # cache issues, see comments inside of get_jobopening_from_path
            current_url = getattr(self.request, 'resolver_match', None)
            jobsconfig = self.get_jobs_config()
            language = get_language_from_request(self.request, check_path=True)
            job_opening = get_jobopening_from_path(
                self.request.path, language, current_url=current_url
            )

            if jobsconfig and can(['add', 'change'], 'jobsconfig'):
                url = admin_reverse('aldryn_jobs_jobsconfig_change',
                                    args=(jobsconfig.pk, ))
                menu.add_modal_item(_('Configure application'), url)

            if can(['add', 'change'], 'jobcategory'):
                if job_opening and job_opening.category:
                    url = admin_reverse('aldryn_jobs_jobcategory_change',
                        args=(job_opening.category.pk, ))
                    menu.add_modal_item(_('Edit category'), url, active=True)

                base_url = admin_reverse('aldryn_jobs_jobcategory_add')
                url = "{base}?app_config={config}".format(
                    base=base_url, config=jobsconfig.pk if jobsconfig else None)
                menu.add_modal_item(_('Add new category'), url)

            if can(['add', 'change'], 'jobopening'):
                if job_opening:
                    url = admin_reverse(
                        'aldryn_jobs_jobopening_change',
                        args=(job_opening.pk,)
                    )
                    menu.add_modal_item(_('Edit job opening'), url, active=True)
                menu.add_modal_item(
                    _('Add new job opening'),
                    admin_reverse('aldryn_jobs_jobopening_add')
                )
