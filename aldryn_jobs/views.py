# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import reversion

from django.db import transaction
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


class JobsBaseMixin(object):
    template_name = 'aldryn_jobs/jobs_list.html'
    model = JobOpening

    def dispatch(self, request, *args, **kwargs):
        # prepare language for misc usage
        self.language = get_language_from_request(request, check_path=True)
        return super(JobsBaseMixin, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Base queryset returns active JobOpenings with respect to language and
        namespace. selects related categories, no ordering.
        """
        # if config is none - probably apphook relaod is in progress, or
        # something is wrong, anyway do not fail with 500
        if self.config is None:
            return JobOpening.objects.none()
        return (
            JobOpening.objects.active()
                              .namespace(self.config.namespace)
                              .language(self.language)
                              .active_translations(self.language)
                              .select_related('category')
        )


class JobOpeningList(JobsBaseMixin, AppConfigMixin, ListView):

    def get_queryset(self):
        return super(JobOpeningList, self).get_queryset().order_by(
            'category__ordering', 'ordering')


class CategoryJobOpeningList(JobsBaseMixin, AppConfigMixin, ListView):
    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        try:
            self.category = (
                JobCategory.objects
                           .language(self.language)
                           .active_translations(self.language,
                                                slug=category_slug)
                           .namespace(self.namespace)
                           .get()
            )
        except JobCategory.DoesNotExist:
            raise Http404

        self.set_language_changer(category=self.category)
        return (super(CategoryJobOpeningList, self).get_queryset()
                .filter(category=self.category)
                .order_by('ordering'))

    def set_language_changer(self, category):
        """Translate the slug while changing the language."""
        set_language_changer(self.request, category.get_absolute_url)


class JobOpeningDetail(AppConfigMixin, TranslatableSlugMixin, DetailView):
    model = JobOpening
    form_class = JobApplicationForm
    template_name = 'aldryn_jobs/jobs_detail.html'
    slug_url_kwarg = 'job_opening_slug'

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

    def get_queryset(self):
        qs = super(JobOpeningDetail, self).get_queryset()
        return qs.namespace(self.namespace)

    @transaction.atomic
    @reversion.create_revision()
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
