# -*- coding: utf-8 -*-
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, ListView

from aldryn_jobs.forms import JobApplicationForm
from aldryn_jobs.models import JobCategory, JobOffer
from menus.utils import set_language_changer


class JobOfferList(ListView):

    template_name = 'aldryn_jobs/job_offer_list.html'

    def get_queryset(self):
        # have to be a method, so the language isn't cached
        return JobOffer.active.language().select_related('category')


class CategoryJobOfferList(JobOfferList):

    def get_queryset(self):
        qs = super(CategoryJobOfferList, self).get_queryset()

        try:
            category = JobCategory.objects.language().get(slug=self.kwargs['category_slug'])
        except JobCategory.DoesNotExist:
            raise Http404

        self.set_language_changer(category=category)
        return qs.filter(category=category)

    def set_language_changer(self, category):
        """Translate the slug while changing the language."""
        set_language_changer(self.request, category.get_absolute_url)


class JobOfferDetail(DetailView):

    template_name = 'aldryn_jobs/job_offer_detail.html'
    slug_url_kwarg = 'job_offer_slug'

    def get_object(self):
        # django-hvad 0.3.0 doesn't support Q conditions in `get` method
        # https://github.com/KristianOellegaard/django-hvad/issues/119
        job_offer = super(JobOfferDetail, self).get_object()
        if not job_offer.get_active():
            raise Http404(_('Offer is not longer valid.'))
        self.set_language_changer(job_offer=job_offer)
        return job_offer

    def get_queryset(self):
        # not active as well, see `get_object` for more detail
        return JobOffer.objects.language().select_related('category')

    def set_language_changer(self, job_offer):
        """Translate the slug while changing the language."""
        set_language_changer(self.request, job_offer.get_absolute_url)

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        self.form = JobApplicationForm(job_offer=self.object)
        return super(JobOfferDetail, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Handles application for the job."""
        self.object = self.get_object()

        if not self.object.can_apply:
            messages.success(self.request, _('You can\'t apply for this job.'))
            return redirect(self.object.get_absolute_url())

        self.form = JobApplicationForm(self.request.POST, self.request.FILES, job_offer=self.object)
        if self.form.is_valid():
            self.form.save()
            msg = _('You\'ve successfully applied for %(job_title)s.') % {'job_title': self.object.title}
            messages.success(self.request, msg)
            return redirect(self.object.get_absolute_url())
        else:
            return super(JobOfferDetail, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(JobOfferDetail, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context
