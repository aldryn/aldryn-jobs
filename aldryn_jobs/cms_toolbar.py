# -*- coding: utf-8 -*-
from aldryn_jobs.models import JobCategory, JobOffer
from django.core.urlresolvers import reverse, resolve
from django.utils.translation import ugettext_lazy as _, \
    get_language_from_request

from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool


def get_joboffer_from_path(path, language):
    current_url = resolve(path)
    category_slug = current_url.kwargs['category_slug']
    job_slug = current_url.kwargs['job_offer_slug']
    if current_url.url_name == 'job-offer-detail':
        job_offer = (
            JobOffer.objects
                    .language(language)
                    .translated('en', slug=job_slug)
                    .filter(category__translations__slug=category_slug,
                            category__translations__language_code=language)
                    .get()
        )
        return job_offer
    return None

@toolbar_pool.register
class JobsToolbar(CMSToolbar):


    def populate(self):
        def can(actions, model):
            if isinstance(actions, basestring):
                actions = [actions]
            for action in actions:
                perm = 'aldryn_jobs.%(action)s_%(model)s' % {
                    'action': action, 'model': model
                }
                if not self.request.user.has_perm(perm):
                    return False
            return True

        if self.is_current_app and (can(['add', 'change'], 'joboffer') or
                                    can(['add', 'change'], 'jobsconfig')):
            menu = self.toolbar.get_or_create_menu('jobs-app', _('Jobs'))
            if can(['add', 'change'], 'joboffer'):
                menu.add_modal_item(
                    _('Add Job Offer'),
                    reverse('admin:aldryn_jobs_joboffer_add')
                )
                language = get_language_from_request(
                    self.request, check_path=True
                )
                job_offer = get_joboffer_from_path(
                    self.request.path, language
                )
                if job_offer:
                    url = reverse(
                        'admin:aldryn_jobs_joboffer_change',
                        args=(job_offer.pk,)
                    )
                    menu.add_modal_item(_('Edit Job Offer'), url, active=True)

            if can(['add', 'change'], 'jobsconfig'):
                url = reverse('admin:aldryn_jobs_jobsconfig_changelist')
                menu.add_sideframe_item(_('Configure Jobs Application'), url)
