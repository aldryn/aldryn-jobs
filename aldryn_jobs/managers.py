from django.db import models
from django.core.urlresolvers import reverse
from django.utils.crypto import get_random_string
from django.contrib.sites.models import get_current_site
from emailit.api import send_mail
from cms.utils.i18n import force_language


class NewsletterSignupManager(models.Manager):
    @staticmethod
    def generate_random_key():
        return get_random_string()

    def active_recipients(self, **kwargs):
        return self.filter(is_verified=True, is_disabled=False, **kwargs)

    def send_job_notifiation(self, recipients=None, job_list=None, current_domain=None):
        if not recipients:
            self.recipient_list = self.active_recipients()
        else:
            self.recipient_list = recipients

        if job_list is None:
            print "Can't send jobs newsletter without job list to be sent."
            return -1

        if current_domain is None:
            request = None
            current_domain = get_current_site(request).domain

        # avoid circular import
        from .models import JobOffer
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
                    'full_link': '{0}{1}'.format(current_domain, job_link)
                })

        sent_emails = 0
        for recipient_user in self.recipient_list:
            kwargs = {'key': recipient_user.confirmation_key}
            link = reverse('unsubscribe_from_newsletter', kwargs=kwargs)
            unsubscribe_link_full = '{0}{1}'.format(current_domain, link)
            context = {
                'jobs': jobs,
                'unsubscribe_link': link,
                'unsubscribe_link_full': unsubscribe_link_full,
            }

            with force_language(recipient_user.default_language):
                sent_emails += send_mail(
                    recipients=[recipient_user.recipient],
                    context=context,
                    template_base='aldryn_jobs/emails/newsletter_job_offers')
        return sent_emails