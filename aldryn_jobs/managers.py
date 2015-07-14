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


class JobOpeningsQuerySet(TranslatableQuerySet):
    def active(self):
        now = timezone.now()
        return self.filter(
            Q(publication_start__isnull=True) | Q(publication_start__lte=now),
            Q(publication_end__isnull=True) | Q(publication_end__gt=now),
            is_active=True
        )


class JobOpeningsManager(TranslatableManager):
    def get_queryset(self):
        return JobOpeningsQuerySet(self.model, using=self.db)

    get_query_set = get_queryset

    def active(self):
        return self.get_queryset().active()
