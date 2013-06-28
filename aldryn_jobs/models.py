# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from cms.models.fields import PlaceholderField
from hvad.models import TranslatableModel, TranslatedFields, TranslationManager


def fetch_translation(record, language):
    """Fetch translation from DB if needed."""
    # can not use hvad.utils.get_translation as it has a fallback for current language - here we don't want that
    if language and language != record.language_code:
        try:
            return record.__class__.objects.language(language_code=language).get(pk=record.pk)
        except models.ObjectDoesNotExist:
            return None
    else:
        return record


class JobCategory(TranslatableModel):

    translations = TranslatedFields(
        name=models.CharField(_('Name'), max_length=255),
        slug=models.SlugField(_('Slug'), max_length=255, blank=True,
                              help_text=_('Auto-generated. Used in the URL. If changed, the URL will change. '
                                          'Clean it to have it re-created.')),
        meta={'unique_together': [['slug', 'language_code']]}
    )

    ordering = models.IntegerField(_('Ordering'), default=0)

    class Meta:
        verbose_name = _('Job category')
        verbose_name_plural = _('Job categories')
        ordering = ['ordering']

    def __unicode__(self):
        return self.lazy_translation_getter('name', str(self.pk))

    def get_absolute_url(self, language=None):
        translation = fetch_translation(self, language)
        if not translation:
            return reverse('job-offer-list')
        kwargs = {
            'category_slug': translation.lazy_translation_getter('slug')
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
        slug=models.SlugField(_('Slug'), max_length=255, blank=True,
                              help_text=_('Auto-generated. Used in the URL. If changed, the URL will change. '
                                          'Clean it to have it re-created.')),
        meta={'unique_together': [['slug', 'language_code']]}
    )

    content = PlaceholderField('Job Offer Content')
    category = models.ForeignKey(JobCategory, verbose_name=_('Category'), related_name='jobs')
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(_('Active'), default=True)
    publication_start = models.DateTimeField(_('Published since'), null=True, blank=True)
    publication_end = models.DateTimeField(_('Published until'), null=True, blank=True)
    can_apply = models.BooleanField(_('Viewer can apply for the job'), default=True)

    objects = TranslationManager()
    active = ActiveJobOffersManager()

    class Meta:
        verbose_name = _('Job offer')
        verbose_name_plural = _('Job offers')
        ordering = ['category__ordering', 'category', '-created']

    def __unicode__(self):
        return self.lazy_translation_getter('title', str(self.pk))

    def get_absolute_url(self, language=None):
        translation = fetch_translation(self, language)
        if not translation:
            return self.category.get_absolute_url(language=language)
        kwargs = {
            'category_slug': translation.category.lazy_translation_getter('slug'),
            'job_offer_slug': translation.lazy_translation_getter('slug'),
        }
        return reverse('job-offer-detail', kwargs=kwargs)

    def get_active(self):
        return all([self.is_active,
                    self.publication_start is None or self.publication_start <= now(),
                    self.publication_end is None or self.publication_end > now()])


upload_to = getattr(settings, 'ALDRYN_JOBS_ATTACHMENTS_UPLOAD_DIR', 'attachments/%Y/%m/')
storage = getattr(settings, 'ALDRYN_JOBS_ATTACHMENTS_STORAGE', None)


class JobApplication(models.Model):

    job_offer = models.ForeignKey(JobOffer)
    first_name = models.CharField(_('First name'), max_length=20)
    last_name = models.CharField(_('Last name'), max_length=20)
    email = models.EmailField(_('E-mail'))
    cover_letter = models.TextField(_('Cover letter'), blank=True)
    attachment = models.FileField(verbose_name=_('Attachment'), blank=True, null=True,
                                  upload_to=upload_to, storage=storage)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __unicode__(self):
        return u'%(first_name)s %(last_name)s' % self.__dict__
