# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import override

from emailit.api import send_mail
from parler.managers import TranslatableManager, TranslatableQuerySet


class JobOffersQuerySet(TranslatableQuerySet):
    def active(self):
        now = timezone.now()
        return self.filter(
            Q(publication_start__isnull=True) | Q(publication_start__lte=now),
            Q(publication_end__isnull=True) | Q(publication_end__gt=now),
            is_active=True
        )


class JobOffersManager(TranslatableManager):
    def get_queryset(self):
        return JobOffersQuerySet(self.model, using=self.db)

    get_query_set = get_queryset

    def active(self):
        return self.get_queryset().active()


class NewsletterSignupManager(models.Manager):
    def generate_random_key(self):
        for trial in range(3):
            new_key = get_random_string()
            if self.filter(confirmation_key=new_key).count() > 0:
                continue
            return new_key
        raise ValueError("Cannot generate unique random confirmation key!")

    def active_recipients(self, **kwargs):
        return self.filter(is_verified=True, is_disabled=False, **kwargs)

    def send_job_notifiation(self, recipients=None, job_list=None,
                             current_domain=None):
        """
        Send job notification emails with respect to app configs. Recipients
        that are registered with specific jobs config / namespace would get only
        job notifications with same jobs config / namespace. This is applicable
        regardless of recipients kwarg is provided or not. If recipients list
        provided (PKs only) NewsletterSignup records would be selected and
        filtered with respect to active recipients (confirmed and not disabled.
        If job_list provided (PKs only) job Offers would be selected. Note that
        job_list is always provided when this method is used through admin
        actions. Returns number of successfully sent emails.
        """
        # avoid circular import
        from .models import JobOpening, NewsletterSignup

        # since this method can and should be also used as a management
        # command. check and warn user that this is required parameter
        # right now it does not makes a lot of sense but in future someone
        # will just change logic here
        if job_list is None:
            # TODO: We probably shouldn't just print to console, who would ever
            # see it?
            print("Can't send jobs newsletter without job list to be sent.")
            # also prevent from hard failures and message admin
            # with error msg.
            return -1

        job_object_list = JobOpening.objects.filter(
            pk__in=job_list).select_related('app_config')
        job_configs = set(job.category.app_config for job in job_object_list)

        recipients_per_config = {}
        if not recipients:
            # get recipients based on selected job offers app configs
            for config in job_configs:
                # TODO: prefetch_related related_user can be added here
                recipients_per_config[config] = self.active_recipients(
                    app_config=config)
        else:
            # otherwise get recipients with respect to job offer app configs.
            recipients_qs = NewsletterSignup.objects.active_recipients(
                pk__in=recipients)
            for config in job_configs:
                found_recipients = recipients_qs.filter(app_config=config)
                recipients_per_config[config] = found_recipients

        if current_domain is None:
            request = None
            current_domain = get_current_site(request).domain

        # TODO: get from settings if we need to send all translations or
        # translations for recipient.default_language (NewsletterSignup) only
        # build links for jobs for all translations
        sent_emails = 0
        for config, recipient_list in recipients_per_config.items():
            jobs = []
            for job in job_object_list.filter(category__app_config=config):
                for job_translation in job.translations.all():
                    # email it appends site on pre mailing so we need to have 2
                    # type of links, full with domain, and relative.
                    job_link = job.get_absolute_url(
                        language=job_translation.language_code)
                    jobs.append({
                        'job': job_translation,
                        'link': job_link,
                        'full_link': '{0}{1}'.format(current_domain, job_link),
                    })

            for recipient_record in recipient_list:
                kwargs = {'key': recipient_record.confirmation_key}
                # prepare a link with respect to user language
                with override(recipient_record.default_language):
                    link = reverse(
                        '{0}:unsubscribe_from_newsletter'.format(
                            recipient_record.app_config.namespace),
                        kwargs=kwargs)
                unsubscribe_link_full = '{0}{1}'.format(current_domain, link)

                context = {
                    'jobs': jobs,
                    'unsubscribe_link': link,
                    'unsubscribe_link_full': unsubscribe_link_full,
                }

                user = recipient_record.related_user.filter(
                    signup__pk=recipient_record.pk)
                if user:
                    user = user.get()
                    context['full_name'] = user.get_full_name()

                sent_successfully = send_mail(
                    recipients=[recipient_record.recipient],
                    context=context,
                    language=recipient_record.default_language,
                    template_base='aldryn_jobs/emails/newsletter_job_offers')

                if sent_successfully:
                    sent_emails += 1
                else:
                    # TODO: we can log or process failures.
                    pass

        return sent_emails
