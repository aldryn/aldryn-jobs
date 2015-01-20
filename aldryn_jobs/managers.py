from django.db import models
from django.utils.crypto import get_random_string


class NewsletterSignupManager(models.Manager):
    def generate_random_key(self):
        return get_random_string()

    def active_recipients(self, **kwargs):
        return self.filter(is_verified=True, is_disabled=False, **kwargs)

    def send_job_notifiation(self, recipients=None):
        if not recipients:
            self.recipient_list = self.active_recipients()
        else:
            self.recipient_list = recipients

        raise NotImplementedError('Waiting for client feedback ;)')