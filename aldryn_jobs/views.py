# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import (
    ugettext as _, get_language_from_request
)
from django.views.generic import DetailView, ListView
from aldryn_apphooks_config.mixins import AppConfigMixin
from aldryn_apphooks_config.utils import get_app_instance
from menus.utils import set_language_changer
from parler.views import TranslatableSlugMixin

from .forms import JobApplicationForm
from .models import JobCategory, JobOpening


class JobOpeningList(AppConfigMixin, ListView):
    template_name = 'aldryn_jobs/jobs_list.html'
    model = JobOpening

    def get_queryset(self):
        # have to be a method, so the language isn't cached
        language = get_language_from_request(self.request, check_path=True)
        return (
            JobOpening.objects.active()
                              .filter(category__app_config=self.config)
                              .language(language)
                              .active_translations(language)
                              .select_related('category')
                              .order_by('category__id')
        )


class CategoryJobOpeningList(JobOpeningList):
    def get_queryset(self):
        qs = super(CategoryJobOpeningList, self).get_queryset()
        language = get_language_from_request(self.request, check_path=True)

        category_slug = self.kwargs['category_slug']
        try:
            self.category = (
                JobCategory.objects
                           .language(language)
                           .active_translations(language, slug=category_slug)
                           .namespace(self.namespace)
                           .get()
            )
        except JobCategory.DoesNotExist:
            raise Http404

        self.set_language_changer(category=self.category)
        return qs.filter(category=self.category)

    def set_language_changer(self, category):
        """Translate the slug while changing the language."""
        set_language_changer(self.request, category.get_absolute_url)


class JobOpeningDetail(AppConfigMixin, TranslatableSlugMixin, DetailView):
    form_class = JobApplicationForm
    template_name = 'aldryn_jobs/jobs_detail.html'
    slug_url_kwarg = 'job_opening_slug'
    queryset = JobOpening.objects.all()

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.namespace, self.config = get_app_instance(request)
        self.object = self.get_object()
        self.set_language_changer(self.object)
        return super(JobOpeningDetail, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return self.form_class

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {'job_opening': self.object}

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_form(self, form_class):
        """
        Returns an instance of the form to be used in this view.
        """
        return form_class(**self.get_form_kwargs())

    def set_language_changer(self, job_opening):
        """Translate the slug while changing the language."""
        set_language_changer(self.request, job_opening.get_absolute_url)

    def get(self, *args, **kwargs):
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)
        return super(JobOpeningDetail, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Handles application for the job."""
        if not self.object.can_apply:
            messages.success(self.request,
                _("You can't apply for this job."))
            return redirect(self.object.get_absolute_url())

        form_class = self.get_form_class()
        self.form = self.get_form(form_class)

        if self.form.is_valid():
            self.form.save()
            msg = _("You have successfully applied for %(job)s.") % {
                'job': self.object.title
            }
            messages.success(self.request, msg)
            return redirect(self.object.get_absolute_url())
        else:
            return super(JobOpeningDetail, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(JobOpeningDetail, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context
