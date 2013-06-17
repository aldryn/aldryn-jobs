# -*- coding: utf-8 -*-
from django.http import Http404
from django.views.generic import DetailView, ListView

from aldryn_jobs.models import JobCategory, JobOffer


class JobOfferMixin(object):

    def get_queryset(self):
        # have to be a method, so the language isn't cached
        return JobOffer.objects.language().select_related('category')


class JobOfferList(JobOfferMixin, ListView):

    template_name = 'aldryn_jobs/job_offer_list.html'


class CategoryJobOfferList(JobOfferList):

    def get_queryset(self):
        try:
            category = JobCategory.objects.language().get(slug=self.kwargs['category_slug'])
        except JobCategory.DoesNotExist:
            raise Http404
        else:
            return super(CategoryJobOfferList, self).get_queryset().filter(category=category)


class JobOfferDetail(JobOfferMixin, DetailView):

    queryset = JobOffer.objects.language().select_related('category')
    template_name = 'aldryn_jobs/job_offer_detail.html'
    slug_url_kwarg = 'job_offer_slug'
