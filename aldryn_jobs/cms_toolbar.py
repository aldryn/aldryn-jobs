# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from cms.toolbar_pool import toolbar_pool


@toolbar_pool.register
def jobs_toolbar(toolbar, request, is_current_app, app_name):

    def can(action, model):
        perm = 'aldryn_jobs.%(action)s_%(model)s' % {'action': action, 'model': model}
        return request.user.has_perm(perm)

    if can('add', 'joboffer') or can('change', 'joboffer'):
        menu = toolbar.get_or_create_menu('jobs-app', _('Jobs'))
        if can('add', 'joboffer'):
            menu.add_modal_item(_('Add Job Offer'), reverse('admin:aldryn_jobs_joboffer_add') + '?_popup')
