# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from cms.models.fields import PlaceholderField
from hvad.models import TranslatableModel, TranslatedFields, TranslationManager


class JobCategory(TranslatableModel):

    translations = TranslatedFields(
        name=models.CharField(_('Name'), max_length=255),
        slug=models.SlugField(_('Slug'), max_length=255)
    )

    ordering = models.IntegerField(_('Ordering'), default=0)

    class Meta:
        verbose_name = _('Job category')
        verbose_name_plural = _('Job categories')
        ordering = ['ordering']

    def __unicode__(self):
        return self.lazy_translation_getter('name', str(self.pk))

    def get_absolute_url(self):
        kwargs = {
            'category_slug': self.lazy_translation_getter('slug')
        }
        return reverse('category-job-offer-list', kwargs=kwargs)


class ActiveJobOffersManager(TranslationManager):

    def using_translations(self):
        qs = super(ActiveJobOffersManager, self).using_translations()
        qs = qs.filter(is_active=True)
        qs = qs.filter(models.Q(publication_start__isnull=True) | models.Q(publication_start__lte=now()))
        qs = qs.filter(models.Q(publication_end__isnull=True) | models.Q(publication_end__gt=now()))
        # bug in hvad - Meta ordering isn't preserved
        qs = qs.order_by('category__ordering', 'category', '-created')
        return qs


class JobOffer(TranslatableModel):

    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255),
        slug=models.SlugField(_('Slug'), max_length=255,
                              help_text=_('Used in the URL. If changed, the URL will change.'))
    )

    content = PlaceholderField('Job Offer Content')
    category = models.ForeignKey(JobCategory, verbose_name=_('Category'), related_name='jobs')
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(_('Active'), default=True)
    publication_start = models.DateTimeField(_('Published Since'), null=True, blank=True)
    publication_end = models.DateTimeField(_('Published Until'), null=True, blank=True)

    objects = TranslationManager()
    active = ActiveJobOffersManager()

    class Meta:
        verbose_name = _('Job offer')
        verbose_name_plural = _('Job offers')
        ordering = ['category__ordering', 'category', '-created']

    def __unicode__(self):
        return self.lazy_translation_getter('title', str(self.pk))

    def get_absolute_url(self):
        kwargs = {
            'category_slug': self.category.safe_translation_getter('slug'),
            'job_offer_slug': self.lazy_translation_getter('slug'),
        }
        return reverse('job-offer-detail', kwargs=kwargs)

    def get_active(self):
        if not self.is_active:
            return False
        if self.publication_start and self.publication_start > now():
            return False
        if self.publication_end and self.publication_end <= now():
            return False
        return True
