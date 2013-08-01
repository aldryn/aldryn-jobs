# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from cms.utils.i18n import force_language, get_current_language
from cms.models.fields import PlaceholderField
from hvad.models import TranslatableModel, TranslatedFields, TranslationManager
from hvad.utils import get_translation

try:
    from django.contrib.auth import get_user_model
except ImportError:  # django < 1.5
    from django.contrib.auth.models import User
else:
    User = get_user_model()


def get_slug_in_language(record, language):
    if not record:
        return None
    if language == record.language_code:  # possibly no need to hit db, try cache
        return record.lazy_translation_getter('slug')
    else:  # hit db
        try:
            translation = get_translation(record, language_code=language)
        except models.ObjectDoesNotExist:
            return None
        else:
            return translation.slug


class JobCategory(TranslatableModel):

    translations = TranslatedFields(
        name=models.CharField(_('Name'), max_length=255),
        slug=models.SlugField(_('Slug'), max_length=255, blank=True,
                              help_text=_('Auto-generated. Used in the URL. If changed, the URL will change. '
                                          'Clean it to have it re-created.')),
        meta={'unique_together': [['slug', 'language_code']]}
    )

    supervisors = models.ManyToManyField(User, verbose_name=_('Supervisors'), related_name='job_offer_categories',
                                         help_text=_('Those people will be notified via e-mail when '
                                                     'new application arrives.'),
                                         blank=True)
    ordering = models.IntegerField(_('Ordering'), default=0)

    class Meta:
        verbose_name = _('Job category')
        verbose_name_plural = _('Job categories')
        ordering = ['ordering']

    def __unicode__(self):
        return self.lazy_translation_getter('name', str(self.pk))

    def get_absolute_url(self, language=None):
        language = language or get_current_language()
        slug = get_slug_in_language(self, language)
        with force_language(language):
            if not slug:
                return reverse('job-offer-list')
            kwargs = {'category_slug': slug}
            return reverse('category-job-offer-list', kwargs=kwargs)

    def get_notification_emails(self):
        return self.supervisors.values_list('email', flat=True)


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
        language = language or get_current_language()
        slug = get_slug_in_language(self, language)
        with force_language(language):
            if not slug:
                return self.category.get_absolute_url(language=language)
            kwargs = {
                'category_slug': get_slug_in_language(self.category, language),
                'job_offer_slug': slug,
            }
            return reverse('job-offer-detail', kwargs=kwargs)

    def get_active(self):
        return all([self.is_active,
                    self.publication_start is None or self.publication_start <= now(),
                    self.publication_end is None or self.publication_end > now()])

    def get_notification_emails(self):
        return self.category.get_notification_emails()


upload_to = getattr(settings, 'ALDRYN_JOBS_ATTACHMENT_UPLOAD_DIR', 'attachments/%Y/%m/')
storage = getattr(settings, 'ALDRYN_JOBS_ATTACHMENT_STORAGE', None)


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
