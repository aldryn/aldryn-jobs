# -*- coding: utf-8 -*-

from django.db.models import Q
from django.utils.timezone import now
from parler.managers import TranslatableManager


class ActiveJobOffersManager(TranslatableManager):
    def apply_custom_filters(self, qs):
        """
        This is provided as a separate method because hvad's using_translations does not call get_query_set.
        """
        qs = qs.filter(is_active=True)
        qs = qs.filter(Q(publication_start__isnull=True) | Q(publication_start__lte=now()))
        qs = qs.filter(Q(publication_end__isnull=True) | Q(publication_end__gt=now()))
        # bug in hvad - Meta ordering isn't preserved
        qs = qs.order_by('category__ordering', 'category', '-created')
        return qs

    def get_query_set(self):
        qs = super(ActiveJobOffersManager, self).get_query_set()
        return self.apply_custom_filters(qs)

    def using_translations(self):
        qs = super(ActiveJobOffersManager, self).using_translations()
        return self.apply_custom_filters(qs)

    def _make_queryset(self, klass, core_filters):
        # Added for >=hvad 0.5.0 compatibility
        qs = super(ActiveJobOffersManager, self)._make_queryset(klass, core_filters)
        import hvad
        if hvad.VERSION >= (0, 5, 0):
            return self.apply_custom_filters(qs)
        return qs
