# -*- coding: utf-8 -*-
from django.http import Http404
from django.views.generic import DetailView, ListView

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
        obj = super(JobOfferDetail, self).get_object()
        if not obj.get_active():
            raise Http404('Offer is not longer valid.')
        self.set_language_changer(job_offer=obj)
        return obj

    def get_queryset(self):
        # not active as well, see `get_object` for more detail
        return JobOffer.objects.language().select_related('category')

    def set_language_changer(self, job_offer):
        """Translate the slug while changing the language."""
        set_language_changer(self.request, job_offer.get_absolute_url)
