# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool

from aldryn_jobs import request_job_offer_identifier


@toolbar_pool.register
class JobsToolbar(CMSToolbar):

    def populate(self):
        def can(action, model):
            perm = 'aldryn_jobs.%(action)s_%(model)s' % {'action': action, 'model': model}
            return self.request.user.has_perm(perm)

        if can('add', 'joboffer') or can('change', 'joboffer'):
            menu = self.toolbar.get_or_create_menu('jobs-app', _('Jobs'))
            if can('add', 'joboffer'):
                menu.add_modal_item(_('Add Job Offer'), reverse('admin:aldryn_jobs_joboffer_add') + '?_popup')

            job_offer = getattr(self.request, request_job_offer_identifier, None)
            if job_offer and can('change', 'joboffer'):
                url = reverse('admin:aldryn_jobs_joboffer_change', args=(job_offer.pk,)) + '?_popup'
                menu.add_modal_item(_('Edit Job Offer'), url, active=True)
