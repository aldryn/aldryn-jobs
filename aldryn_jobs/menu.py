# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import ugettext_lazy as _

from cms.menu_bases import CMSAttachMenu
from cms.utils import get_language_from_request
from menus.base import NavigationNode
from menus.menu_pool import menu_pool

from .models import JobCategory
from .models import JobOffer


class JobCategoryMenu(CMSAttachMenu):

    name = _('Job Categories')

    def get_nodes(self, request):
        try:
            app_namespace = self.instance.application_namespace
        except AttributeError:
            app_namespace = None
        language = get_language_from_request(request)
        nodes = []
        categories = (
            JobCategory.objects.namespace(app_namespace)
                               .language(language)
                               .translated(language)
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


class JobOfferMenu(CMSAttachMenu):

    name = _("Job Offers Menu")

    def get_nodes(self, request):

        try:
            app_namespace = self.instance.application_namespace
        except AttributeError:
            app_namespace = None

        current_language = get_language_from_request(request)
        nodes = []
        offers = (
            JobOffer.objects.active()
                            .namespace(app_namespace)
                            .language(current_language)
                            .translated(current_language)
        )
        for job_offer in offers:
            try:
                node = NavigationNode(
                    title=job_offer.title,
                    url=job_offer.get_absolute_url(),
                    id=job_offer.pk,
                )
            except NoReverseMatch:
                pass
            else:
                nodes.append(node)
        return nodes


menu_pool.register_menu(JobCategoryMenu)
menu_pool.register_menu(JobOfferMenu)
