# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import ugettext_lazy as _

from cms.menu_bases import CMSAttachMenu
from cms.utils import get_language_from_request
from menus.base import NavigationNode
from menus.menu_pool import menu_pool

from .models import JobCategory
from .models import JobOpening


class JobCategoryMenu(CMSAttachMenu):

    name = _("Job Categories Menu")

    def get_nodes(self, request):
        try:
            app_namespace = self.instance.application_namespace
        except AttributeError:
            app_namespace = None
        language = get_language_from_request(request)
        nodes = []
        categories = (
            JobCategory.objects
                       .namespace(app_namespace)
                       .language(language)
                       .active_translations(language)
        )
        for category in categories:
            try:
                node = NavigationNode(category.name,
                                      category.get_absolute_url(),
                                      category.slug)
                nodes.append(node)
            except NoReverseMatch:
                pass
        return nodes


class JobOpeningMenu(CMSAttachMenu):

    name = _("Job Openings Menu")

    def get_nodes(self, request):

        try:
            app_namespace = self.instance.application_namespace
        except AttributeError:
            app_namespace = None

        current_language = get_language_from_request(request)
        nodes = []
        openings = (
            JobOpening.objects
                      .active()
                      .namespace(app_namespace)
                      .language(current_language)
                      .active_translations(current_language)
        )
        for job_opening in openings:
            try:
                node = NavigationNode(
                    title=job_opening.title,
                    url=job_opening.get_absolute_url(),
                    id=job_opening.pk,
                )
            except NoReverseMatch:
                pass
            else:
                nodes.append(node)
        return nodes


menu_pool.register_menu(JobCategoryMenu)
menu_pool.register_menu(JobOpeningMenu)
