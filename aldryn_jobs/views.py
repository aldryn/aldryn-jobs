# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import redirect, render, render_to_response
from django.template import RequestContext
from django.utils.translation import pgettext
from django.views.generic import CreateView, DetailView, ListView, TemplateView, View
from django.views.generic.base import TemplateResponseMixin
from django.utils.translation import ugettext_lazy as _
from menus.utils import set_language_changer

from cms.utils.i18n import get_default_language
from emailit.api import send_mail

from . import request_job_offer_identifier
from .forms import (
    JobApplicationForm, NewsletterConfirmationForm,NewsletterSignupForm,
    NewsletterUnsubscriptionForm, NewsletterResendConfirmationForm
)
from .models import (
    JobCategory, JobOffer, NewsletterSignup,JobNewsletterRegistrationPlugin
)


class JobOfferList(ListView):
    template_name = 'aldryn_jobs/jobs_list.html'

    def get_queryset(self):
        # have to be a method, so the language isn't cached
        return (JobOffer.active.language().select_related('category')
                .order_by('category__id'))


class CategoryJobOfferList(JobOfferList):
    def get_queryset(self):
        qs = super(CategoryJobOfferList, self).get_queryset()

        try:
            category = JobCategory.objects.language().get(
                slug=self.kwargs['category_slug'])
        except JobCategory.DoesNotExist:
            raise Http404

        self.set_language_changer(category=category)
        return qs.filter(category=category)

    def set_language_changer(self, category):
        """Translate the slug while changing the language."""
        set_language_changer(self.request, category.get_absolute_url)


class JobOfferDetail(DetailView):
    form_class = JobApplicationForm
    template_name = 'aldryn_jobs/jobs_detail.html'
    slug_url_kwarg = 'job_offer_slug'

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.object = self.get_object()
        return super(JobOfferDetail, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        # django-hvad 0.3.0 doesn't support Q conditions in `get` method
        # https://github.com/KristianOellegaard/django-hvad/issues/119
        job_offer = super(JobOfferDetail, self).get_object()
        if not job_offer.get_active() and not self.request.user.is_staff:
            raise Http404(
                pgettext('aldryn-jobs', 'Offer is not longer valid.'))
        setattr(self.request, request_job_offer_identifier, job_offer)
        self.set_language_changer(job_offer=job_offer)
        return job_offer

    def get_form_class(self):
        return self.form_class

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {'job_offer': self.object}

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

    def get_queryset(self):
        # not active as well, see `get_object` for more detail
        return JobOffer.objects.language().select_related('category')

    def set_language_changer(self, job_offer):
        """Translate the slug while changing the language."""
        set_language_changer(self.request, job_offer.get_absolute_url)

    def get(self, *args, **kwargs):
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)
        return super(JobOfferDetail, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Handles application for the job."""

        if not self.object.can_apply:
            messages.success(self.request, pgettext('aldryn-jobs',
                                                    'You can\'t apply for this job.'))
            return redirect(self.object.get_absolute_url())

        form_class = self.get_form_class()
        self.form = self.get_form(form_class)

        if self.form.is_valid():
            self.form.save()
            msg = pgettext('aldryn-jobs',
                           'You have successfully applied for %(job)s.') % {
                      'job': self.object.title}
            messages.success(self.request, msg)
            return redirect(self.object.get_absolute_url())
        else:
            return super(JobOfferDetail, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(JobOfferDetail, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context


class ConfirmNewsletterSignup(TemplateResponseMixin, View):
    http_method_names = ["get", "post"]
    messages = {
        "key_confirmed": {
            "level": messages.SUCCESS,
            "text": _("You have confirmed {email}.")
        }
    }
    form_class = NewsletterConfirmationForm

    def get_template_names(self):
        return {
            "GET": ["aldryn_jobs/newsletter_confirm.html"],
            "POST": ["aldryn_jobs/newsletter_confirmed.html"],
        }[self.request.method]

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        # if recipient already confirmed his email then there is
        # a high chance that this is a brute force attack
        if self.object.is_verified:
            raise Http404()
        ctx = self.get_context_data()
        # populate form with key
        form_class = self.get_form_class()
        ctx['form'] = form_class(
            initial={'confirmation_key': self.kwargs['key']})
        return self.render_to_response(ctx)

    def post(self, *args, **kwargs):
        form_class = self.get_form_class()
        form = form_class(self.request.POST)
        if form.is_valid():
            form_confirmation_key = form.cleaned_data['confirmation_key']

            try:
                self.object = NewsletterSignup.objects.get(
                    confirmation_key=form_confirmation_key)
            except NewsletterSignup.DoesNotExist:
                return HttpResponseRedirect(reverse('confirm_newsletter_not_found'))

        # do not confirm second time
        if not self.object.is_verified:
            self.object.confirm()
            self.after_confirmation(self.object)

        redirect_url = self.get_redirect_url()
        if not redirect_url:
            ctx = self.get_context_data()
            return self.render_to_response(ctx)

        if self.messages.get("key_confirmed"):
            messages.add_message(
                self.request,
                self.messages["key_confirmed"]["level"],
                self.messages["key_confirmed"]["text"].format(**{
                    "email": self.object.recipient
                })
            )
        return redirect(redirect_url)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return queryset.filter(
                confirmation_key=self.kwargs["key"])[:1].get()
            # Until the model-field is not set to unique=True,
            # we'll use the trick above
        except NewsletterSignup.DoesNotExist:
            raise Http404()

    def get_queryset(self):
        qs = NewsletterSignup.objects.all()
        return qs

    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx["confirmation"] = self.object
        return ctx

    def get_form_class(self):
        return self.form_class

    def get_redirect_url(self):
        """ Implement this for custom redirects """
        return None

    def after_confirmation(self, signup):
        """ Implement this for custom post-save operations """
        # FIXME: does not distinct between plugin instances, and draft/published pages
        all_groups = set(
            [group for plugin in
                JobNewsletterRegistrationPlugin.objects.all()
             for group in plugin.mail_to_group.all()]
        )
        admin_recipients = set([user.email for group in all_groups
                                for user in group.user_set.all()])

        additional_recipients = getattr(settings, 'ALDRYN_JOBS_NEWSLETTER_ADDITIONAL_NOTIFICATION_EMAILS')
        if additional_recipients:
            admin_recipients.update(additional_recipients)

        context = {
            'new_recipient': signup.recipient
        }
        for admin_recipient in admin_recipients:
            send_mail(
                recipients=[admin_recipient],
                context=context,
                template_base='aldryn_jobs/emails/newsletter_new_recipient')


class UnsubscibeNewsletterSignup(TemplateResponseMixin, View):
    http_method_names = ["get", "post"]

    def get_template_names(self):
        return {
            "GET": ["aldryn_jobs/newsletter_unsubscribe.html"],
            "POST": ["aldryn_jobs/newsletter_unsubscribed.html"],
        }[self.request.method]

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        # if object is disabled - do not serve this page
        if self.object.is_disabled:
            raise Http404()
        ctx = self.get_context_data()
        # populate form with key
        ctx['form'] = NewsletterUnsubscriptionForm(
            initial={'confirmation_key': self.kwargs['key']})
        return self.render_to_response(ctx)

    def post(self, *args, **kwargs):
        form = NewsletterUnsubscriptionForm(self.request.POST)
        if form.is_valid():
            form_confirmation_key = form.cleaned_data['confirmation_key']

            try:
                self.object = NewsletterSignup.objects.get(
                    confirmation_key=form_confirmation_key)
            except NewsletterSignup.DoesNotExist:
                return HttpResponseRedirect(reverse('confirm_newsletter_not_found'))

        # do not confirm second time
        if not self.object.is_disabled:
            self.object.disable()
            # run custom actions, if there is
            self.after_unsubscription(self.object)

        redirect_url = self.get_redirect_url()
        if not redirect_url:
            ctx = self.get_context_data()
            return self.render_to_response(ctx)

        return redirect(redirect_url)

    # for flexibility
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            return queryset.filter(
                confirmation_key=self.kwargs["key"])[:1].get()
            # Until the model-field is not set to unique=True,
            # we'll use the trick above
        except NewsletterSignup.DoesNotExist:
            raise Http404()

    def get_queryset(self):
        qs = NewsletterSignup.objects.all()
        return qs

    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx["confirmation"] = self.object
        return ctx

    def get_redirect_url(self):
        """ Implement this for custom redirects """
        return None

    def after_unsubscription(self, signup):
        """ Implement this for custom post-save operations """
        # raise NotImplementedError()
        pass


class RegisterJobNewsletter(CreateView):

    def get(self, request, *args, **kwargs):
        # TODO: add GET requests registration functionality
        # don't serve get requests, only plugin registration so far
        return HttpResponsePermanentRedirect(reverse('job-offer-list'))

    def get_invalid_template_name(self):
        return 'aldryn_jobs/newsletter_invalid_email.html'

    def get_form_class(self):
        return NewsletterSignupForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # populate object with other data
        if self.request.user.is_authenticated():
            # in memory only property, will be used just for confirmation email
            self.object.user = self.request.user

        self.object.confirmation_key = NewsletterSignup.objects.generate_random_key()
        # try to get language
        if self.request.LANGUAGE_CODE:
            self.object.default_language = self.request.LANGUAGE_CODE
        else:
            self.object.default_language = get_default_language()

        self.object.save()
        self.object.send_newsletter_confirmation_email()
        return super(RegisterJobNewsletter, self).form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        # check if user needs a resend confirmation link
        recipient_email = form.data.get('recipient')
        recipient_object = NewsletterSignup.objects.filter(recipient=recipient_email)
        # check for registered but not confirmed
        context['resend_confirmation'] = None
        if recipient_email is not None and recipient_object:
            recipient_object = recipient_object[0]
            context['resend_confirmation'] = reverse('resend_confirmation_link', kwargs={
                'key': recipient_object.confirmation_key})
        template_name = self.template_invalid_name if (
            hasattr(self, 'template_invalid_name')) else (
            self.get_invalid_template_name())
        context_instance = RequestContext(self.request, context)
        return render(self.request, template_name=template_name, context_instance=context_instance)

    def get_success_url(self):
        return reverse('newsletter_registration_notification')


class ResendNewsletterConfirmation(ConfirmNewsletterSignup):
    form_class = NewsletterResendConfirmationForm

    def get_template_names(self):
        return {
            "GET": ["aldryn_jobs/newsletter_resend_confirmation.html"],
            "POST": ["aldryn_jobs/newsletter_confirmation_resent.html"],
        }[self.request.method]

    def post(self, *args, **kwargs):
        form_class = self.get_form_class()
        form = form_class(self.request.POST)
        if form.is_valid():
            form_confirmation_key = form.cleaned_data['confirmation_key']

            try:
                self.object = NewsletterSignup.objects.get(
                    confirmation_key=form_confirmation_key)
            except NewsletterSignup.DoesNotExist:
                return HttpResponseRedirect(reverse('confirm_newsletter_not_found'))

        self.object = self.get_object()
        self.object.reset_confirmation()

        redirect_url = self.get_redirect_url()
        if not redirect_url:
            ctx = self.get_context_data()
            return self.render_to_response(ctx)

        return redirect(redirect_url)


class ConfirmNewsletterNotFound(TemplateView):
    template_name = 'aldryn_jobs/newsletter_confirm_not_found.html'


class SuccessRegistrationMessage(TemplateView):
    template_name = 'aldryn_jobs/registered_for_newsletter.html'