# -*- coding: utf-8 -*-
from aldryn_apphooks_config.mixins import AppConfigMixin
from aldryn_apphooks_config.utils import get_app_instance

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import (
    Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
)
from django.shortcuts import redirect, render, render_to_response
from django.template import RequestContext
from django.utils.translation import (
    pgettext_lazy as _, get_language_from_request
)
from django.views.generic import (
    CreateView, DetailView, ListView, TemplateView, View
)
from django.views.generic.base import TemplateResponseMixin

from cms.utils.i18n import get_default_language
from emailit.api import send_mail
from menus.utils import set_language_changer

from .forms import (
    JobApplicationForm, NewsletterConfirmationForm, NewsletterSignupForm,
    NewsletterUnsubscriptionForm, NewsletterResendConfirmationForm
)
from .models import (
    JobCategory, JobOffer, NewsletterSignup, JobNewsletterRegistrationPlugin,
    NewsletterSignupUser, JobsConfig,
)


class JobOfferList(AppConfigMixin, ListView):
    template_name = 'aldryn_jobs/jobs_list.html'
    model = JobOffer

    def get_queryset(self):
        # have to be a method, so the language isn't cached
        language = get_language_from_request(self.request, check_path=True)
        return (
            JobOffer.objects.active()
                            .language(language)
                            .translated(language)
                            .select_related('category')
                            .namespace(self.namespace)
                            .order_by('category__id')
        )


class CategoryJobOfferList(JobOfferList):

    def get_queryset(self):
        qs = super(CategoryJobOfferList, self).get_queryset()
        language = get_language_from_request(self.request, check_path=True)

        category_slug = self.kwargs['category_slug']
        try:
            self.category = (
                JobCategory.objects.language(language)
                                   .translated(language, slug=category_slug)
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


class JobOfferDetail(AppConfigMixin, DetailView):
    form_class = JobApplicationForm
    template_name = 'aldryn_jobs/jobs_detail.html'
    slug_url_kwarg = 'job_offer_slug'

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.namespace, self.config = get_app_instance(request)
        self.object = self.get_object()
        self.set_language_changer(self.object)
        return super(JobOfferDetail, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        slug = self.kwargs.get(self.slug_url_kwarg, None)
        slug_field = self.get_slug_field()
        language = get_language_from_request(self.request, check_path=True)
        queryset = (
            queryset.namespace(self.namespace)
                    .language(language)
                    .translated(language, **{slug_field: slug})
        )

        job_offer = None
        try:
            job_offer = queryset.get()
        except JobOffer.DoesNotExist:
            pass
        finally:
            if (not job_offer or (not job_offer.get_active() and
                                  not self.request.user.is_staff)):
                raise Http404(_(
                    'aldryn-jobs', 'Offer is not longer valid.'
                ))
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
        language = get_language_from_request(self.request, check_path=True)
        return (
            JobOffer.objects.language(language)
                            .translated(language)
                            .select_related('category')
        )

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
            messages.success(
                self.request,
                _('aldryn-jobs', 'You can\'t apply for this job.')
            )
            return redirect(self.object.get_absolute_url())

        form_class = self.get_form_class()
        self.form = self.get_form(form_class)

        if self.form.is_valid():
            self.form.save()
            msg = (
                _('aldryn-jobs', 'You have successfully applied for %(job)s.')
                % {'job': self.object.title}
            )
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
            "text": _('aldryn-jobs', "You have confirmed {email}.")
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
        if self.object.is_verified and not self.object.is_disabled:
            raise Http404()
        ctx = self.get_context_data()
        # populate form with key
        form_class = self.get_form_class()
        ctx['form'] = form_class(
            initial={'confirmation_key': self.kwargs['key']})
        return self.render_to_response(ctx)

    def post(self, *args, **kwargs):
        form_class = self.get_form_class()
        form_confirmation_key = self.request.POST.get('confirmation_key')
        # since we using a form and have a unique constraint on confirmation
        # key we need to get instance before validating the form
        try:
            instance = NewsletterSignup.objects.get(
                confirmation_key=form_confirmation_key,
                is_verified=False)
        except NewsletterSignup.DoesNotExist:
            raise Http404()
        form = form_class(self.request.POST, instance=instance)
        if form.is_valid():
            self.object = instance
            # do not confirm second time
            if not self.object.is_verified:
                self.object.confirm()
                self.after_confirmation(self.object)
        else:
            # be careful if you add custom fields on confirmation form
            # validate errors will cause a 404.
            raise Http404()

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
        # eventually we don't have abilities right now to track which plugin
        # was used to register for newsletter, so we will use all matching
        # plugins with filtering by language and app_config
        plugins_base_qs = signup.app_config.jobnewsletterregistrationplugin_set.filter(
            language=signup.default_language)
        # also do not use draft settings, only plugins from public pages
        # plugin page.pk should match page.get_public_object().pk
        public_plugins = [plugin for plugin in plugins_base_qs if (
            plugin.page.get_public_object() and
            plugin.page.pk == plugin.page.get_public_object().pk)]

        public_plugins_groups = set(
            [group for plugin in
                public_plugins
             for group in plugin.mail_to_group.all()]
        )
        # eventually get emails of users from matching groups
        admin_recipients = set(
            [user.email for group in public_plugins_groups
                for user in group.user_set.all()])

        # if we have something special from settings - also use those lists
        # of addresses to notify about successful user registration
        additional_recipients = getattr(
            settings, 'ALDRYN_JOBS_NEWSLETTER_ADDITIONAL_NOTIFICATION_EMAILS',
            [])
        additional_recipients += getattr(
            settings, 'ALDRYN_JOBS_DEFAULT_SEND_TO', [])

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
    form_class = NewsletterUnsubscriptionForm

    def get_template_names(self):
        return {
            "GET": ["aldryn_jobs/newsletter_unsubscribe.html"],
            "POST": ["aldryn_jobs/newsletter_unsubscribed.html"],
        }[self.request.method]

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        # if object is disabled - do not serve this page
        if self.object.is_disabled or not self.object.is_verified:
            raise Http404()
        ctx = self.get_context_data()
        # populate form with key
        form_class = self.get_form_class()
        ctx['form'] = form_class(
            initial={'confirmation_key': self.kwargs['key']})
        return self.render_to_response(ctx)

    def post(self, *args, **kwargs):
        form_confirmation_key = self.request.POST.get('confirmation_key')
        # since we using a form and have a unique constraint on confirmation
        # key we need to get instance before validating the form
        try:
            instance = NewsletterSignup.objects.active_recipients().get(
                confirmation_key=form_confirmation_key)
        except NewsletterSignup.DoesNotExist:
            raise Http404()

        form_class = self.get_form_class()
        form = form_class(self.request.POST, instance=instance)

        if form.is_valid():
            self.object = instance
            # do not confirm second time
            if not self.object.is_disabled:
                self.object.disable()
                # run custom actions, if there is
                self.after_unsubscription(self.object)
        else:
            # be careful if you add custom fields on confirmation form
            # validate errors will cause a 404.
            raise Http404()

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
            return queryset.get(confirmation_key=self.kwargs["key"])
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

    def after_unsubscription(self, signup):
        """ Implement this for custom post-save operations """
        # raise NotImplementedError()
        pass


class RegisterJobNewsletter(CreateView):
    form_class = NewsletterSignupForm

    def dispatch(self, request, *args, **kwargs):
        namespace = ''
        resolver_match = getattr(self.request, 'resolver_match', None)
        if resolver_match is not None:
            namespace = getattr(resolver_match, 'namespace', '')

        if len(namespace) < 1:
            if (self.request.current_page and
                    self.request.current_page.application_namespace):
                namespace = self.request.current_page.application_namespace

        if len(namespace) < 1:
            raise ImproperlyConfigured(
                "Cant find name space, please either fix it "
                "or enable cms CurrentPage middleware")
        # in memory thing, we need it for form processing etc.
        # FIXME: unfortunately app config namespace is not unique,
        # using only first match
        app_config = JobsConfig.objects.filter(namespace=namespace)
        if app_config:
            app_config = app_config[0]
        self.app_config = app_config

        return super(RegisterJobNewsletter, self).dispatch(request,
                                                           *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # TODO: add GET requests registration functionality
        # don't serve get requests, only plugin registration so far
        return HttpResponsePermanentRedirect(
            reverse('{0}:job-offer-list'.format(self.app_config.namespace)))

    def get_invalid_template_name(self):
        return 'aldryn_jobs/newsletter_invalid_email.html'

    def get_form_kwargs(self):
        kwargs = super(RegisterJobNewsletter, self).get_form_kwargs()
        kwargs.update({'app_config': self.app_config})
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.confirmation_key = NewsletterSignup.objects.generate_random_key()

        # try to get language
        if getattr(self.request, 'LANGUAGE_CODE', None) is not None:
            self.object.default_language = self.request.LANGUAGE_CODE
        else:
            self.object.default_language = get_language_from_request(
                self.request, check_path=True)

        # populate object with other data
        self.object.app_config = self.app_config
        user = self.request.user if self.request.user.is_authenticated() else None
        if user is not None:
            # in memory only property, will be used just for confirmation email
            self.object.user = user
        self.object.save()

        if user:
            NewsletterSignupUser.objects.create(
                signup=self.object, user=user)

        self.object.send_newsletter_confirmation_email(request=self.request)
        return super(RegisterJobNewsletter, self).form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        context['app_config'] = self.app_config
        # check if user needs a resend confirmation link
        recipient_email = form.data.get('recipient')
        recipient_object = NewsletterSignup.objects.filter(
            recipient=recipient_email)
        # check for registered but not confirmed
        context['resend_confirmation'] = None
        if recipient_email is not None and recipient_object:
            recipient_object = recipient_object[0]
            context['resend_confirmation'] = reverse(
                '{0}:resend_confirmation_link'.format(
                    self.app_config.namespace),
                kwargs={'key': recipient_object.confirmation_key})
        template_name = self.template_invalid_name if (
            hasattr(self, 'template_invalid_name')) else (
            self.get_invalid_template_name())
        context_instance = RequestContext(self.request, context)
        return render(self.request, template_name=template_name,
                      context_instance=context_instance)

    def get_success_url(self):
        return reverse('{0}:newsletter_registration_notification'.format(
            self.app_config.namespace))


class ResendNewsletterConfirmation(ConfirmNewsletterSignup):
    form_class = NewsletterResendConfirmationForm

    def get_template_names(self):
        return {
            "GET": ["aldryn_jobs/newsletter_resend_confirmation.html"],
            "POST": ["aldryn_jobs/newsletter_confirmation_resent.html"],
        }[self.request.method]

    def post(self, *args, **kwargs):
        form_confirmation_key = self.request.POST.get('confirmation_key')
        try:
            self.object = NewsletterSignup.objects.get(
                confirmation_key=form_confirmation_key)
        except NewsletterSignup.DoesNotExist:
            raise Http404()
        form_class = self.get_form_class()
        form = form_class(self.request.POST, instance=self.object)

        if form.is_valid():
            self.object.reset_confirmation()

        redirect_url = self.get_redirect_url()
        if not redirect_url:
            ctx = self.get_context_data()
            return self.render_to_response(ctx)

        return redirect(redirect_url)


class SuccessRegistrationMessage(TemplateView):
    template_name = 'aldryn_jobs/registered_for_newsletter.html'
