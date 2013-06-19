# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from aldryn_jobs.models import JobCategory

from cms.menu_bases import CMSAttachMenu
from menus.base import NavigationNode
from menus.menu_pool import menu_pool


class JobCategoryMenu(CMSAttachMenu):

    name = _('Job Categories')

    def get_nodes(self, request):
        nodes = []
        categories = JobCategory.objects.language()
        # bug in hvad - Meta ordering isn't preserved
        categories = categories.order_by('ordering')
        for category in categories:
            node = NavigationNode(category.name,
                                  category.get_absolute_url(),
                                  category.slug)
            nodes.append(node)
        return nodes

menu_pool.register_menu(JobCategoryMenu)
