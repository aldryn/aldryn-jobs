# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Q
from django.utils import timezone

from parler.managers import TranslatableManager, TranslatableQuerySet


class JobOpeningsQuerySet(TranslatableQuerySet):
    def active(self):
        now = timezone.now()
        return self.filter(
            Q(publication_start__isnull=True) | Q(publication_start__lte=now),
            Q(publication_end__isnull=True) | Q(publication_end__gt=now),
            is_active=True
        )

    def namespace(self, namespace):
        return self.filter(category__app_config__namespace=namespace)


class JobOpeningsManager(TranslatableManager):
    def get_queryset(self):
        return JobOpeningsQuerySet(self.model, using=self.db)

    get_query_set = get_queryset

    def active(self):
        return self.get_queryset().active()

    def namespace(self, namespace):
        return self.get_query_set().namespace(namespace)
