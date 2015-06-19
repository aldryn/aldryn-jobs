# -*- coding: utf-8 -*-
from aldryn_apphooks_config.managers.parler import \
    AppHookConfigTranslatableManager, AppHookConfigTranslatableQueryset

from django.db.models import Q
from django.utils import timezone
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.crypto import get_random_string
from django.utils.translation import override
from django.contrib.sites.models import get_current_site
from emailit.api import send_mail


class JobOffersQuerySet(AppHookConfigTranslatableQueryset):

    def active(self):
        now = timezone.now()
        return self.filter(
            Q(publication_start__isnull=True) | Q(publication_start__lte=now),
            Q(publication_end__isnull=True) | Q(publication_end__gt=now),
            is_active=True
        )


class JobOffersManager(AppHookConfigTranslatableManager):

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

    def send_job_notifiation(self, recipients=None, job_list=None, current_domain=None):
        # avoid circular import
        from .models import JobOffer

        if not recipients:
            self.recipient_list = self.active_recipients()
        else:
            self.recipient_list = recipients

        # since this method can and should be also used as a management
        # command. check and warn user that this is required parameter
        # right now it does not makes a lot of sense but in future someone
        # will just change logic here
        if job_list is None:
            print "Can't send jobs newsletter without job list to be sent."
            # also prevent from hard failures and message admin
            # with error msg.
            return -1

        if current_domain is None:
            request = None
            current_domain = get_current_site(request).domain

        job_object_list = JobOffer.objects.filter(pk__in=job_list)

        # TODO: get from settings if we need to send all translations or
        # translations for recipient.default_language (NewsletterSignup) only
        # build links for jobs for all translations
        jobs = []
        for job in job_object_list:
            for job_translation in job.translations.all():
                # email it appends site on pre mailing so we need to have 2 type
                # of links, full with domain, and relative.
                job_link = job.get_absolute_url(
                    language=job_translation.language_code)
                jobs.append({
                    'job': job_translation,
                    'link': job_link,
                    'full_link': '{0}{1}'.format(current_domain, job_link),
                })

        sent_emails = 0
        for recipient_record in self.recipient_list:
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

            user = recipient_record.related_user.filter(signup__pk=recipient_record.pk)
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
