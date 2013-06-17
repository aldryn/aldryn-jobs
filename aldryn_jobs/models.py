# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models.fields import PlaceholderField
from hvad.models import TranslatableModel, TranslatedFields


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
        return self.safe_translation_getter('name', str(self.pk))

    def get_absolute_url(self):
        kwargs = {
            'category_slug': self.safe_translation_getter('slug')
        }
        return reverse('category-job-offer-list', kwargs=kwargs)


class JobOffer(TranslatableModel):

    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255),
        slug=models.SlugField(_('Slug'), max_length=255)
    )

    content = PlaceholderField('Job Offer Content')
    category = models.ForeignKey(JobCategory, verbose_name=_('Category'), related_name='jobs')
    active = models.BooleanField(_('Active'), default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Job offer')
        verbose_name_plural = _('Job offers')
        ordering = ['category', '-created']

    def __unicode__(self):
        return self.safe_translation_getter('title', str(self.pk))

    def get_absolute_url(self):
        kwargs = {
            'category_slug': self.category.safe_translation_getter('slug'),
            'job_offer_slug': self.safe_translation_getter('slug'),
        }
        return reverse('job-offer-detail', kwargs=kwargs)
