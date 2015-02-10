# -*- coding: utf-8 -*-

from django import get_version
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin
from cms.models.fields import PlaceholderField
from cms.utils.i18n import force_language, get_current_language
from distutils.version import StrictVersion
from djangocms_text_ckeditor.fields import HTMLField
from functools import partial
from os.path import join as join_path
from uuid import uuid4

from parler.models import TranslatableModel, TranslatedFields

from .managers import ActiveJobOffersManager
from .utils import get_valid_filename


def get_user_model_for_fields():
    if StrictVersion(get_version()) < StrictVersion('1.6.0'):
        from django.contrib.auth.models import User
    else:
        return settings.AUTH_USER_MODEL


def default_jobs_attachment_upload_to(instance, filename):
    date = now().strftime('%Y/%m')
    return join_path(
        'attachments', date, str(uuid4()), get_valid_filename(filename)
    )


jobs_attachment_upload_to = getattr(
    settings, 'ALDRYN_JOBS_ATTACHMENT_UPLOAD_DIR',
    default_jobs_attachment_upload_to
)

jobs_attachment_storage = getattr(
    settings, 'ALDRYN_JOBS_ATTACHMENT_STORAGE', None
)

JobApplicationFileField = partial(
    models.FileField,
    max_length=200,
    blank=True,
    null=True,
    upload_to=jobs_attachment_upload_to,
    storage=jobs_attachment_storage
)


class JobCategory(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(_('Name'), max_length=255),
        slug=models.SlugField(
            _('Slug'), max_length=255, blank=True,
            help_text=_('Auto-generated. Used in the URL. If changed, the URL'
                        ' will change. Clean it to have it re-created.')
        ),
        meta={'unique_together': [['slug', 'language_code']]}
    )

    supervisors = models.ManyToManyField(
        get_user_model_for_fields(), verbose_name=_('Supervisors'),
        related_name='job_offer_categories',
        help_text=_('Those people will be notified via e-mail when new '
                    'application arrives.'),
        blank=True
    )
    ordering = models.IntegerField(_('Ordering'), default=0)

    class Meta:
        verbose_name = _('Job category')
        verbose_name_plural = _('Job categories')
        ordering = ['ordering']

    def __unicode__(self):
        return self.safe_translation_getter('name', str(self.pk))

    def get_absolute_url(self, language=None):
        language = language or get_current_language()
        slug = self.safe_translation_getter('slug', language_code=language)
        with force_language(language):
            try:
                if not slug:
                    return reverse('job-offer-list')
                kwargs = {'category_slug': slug}
                return reverse('category-job-offer-list', kwargs=kwargs)
            except NoReverseMatch:
                return "/%s/" % language

    def get_notification_emails(self):
        return self.supervisors.values_list('email', flat=True)


class JobOffer(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255),
        slug=models.SlugField(
            _('Slug'), max_length=255, blank=True,
            help_text=_('Auto-generated. Used in the URL. If changed, the URL '
                        'will change. Clean it to have it re-created.')
        ),
        lead_in=HTMLField(
            _('Lead in'), blank=True,
            help_text=_('Will be displayed in lists')
        ),
        meta={'unique_together': [['slug', 'language_code']]}
    )

    content = PlaceholderField('Job Offer Content')
    category = models.ForeignKey(
        JobCategory, verbose_name=_('Category'), related_name='jobs'
    )
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(_('Active'), default=True)
    publication_start = models.DateTimeField(
        _('Published since'), null=True, blank=True
    )
    publication_end = models.DateTimeField(
        _('Published until'), null=True, blank=True
    )
    can_apply = models.BooleanField(
        _('Viewer can apply for the job'), default=True
    )

    active = ActiveJobOffersManager()

    class Meta:
        verbose_name = _('Job offer')
        verbose_name_plural = _('Job offers')
        ordering = ['category__ordering', 'category', '-created']

    def __unicode__(self):
        return self.safe_translation_getter('title', str(self.pk))

    def get_absolute_url(self, language=None):
        language = language or get_current_language()
        slug = self.safe_translation_getter('slug', language_code=language)
        category_slug = self.category.safe_translation_getter(
            'slug', language_code=language
        )

        with force_language(language):
            try:
                if not slug:
                    return self.category.get_absolute_url(language=language)
                kwargs = {
                    'category_slug': category_slug,
                    'job_offer_slug': slug,
                }
                return reverse('job-offer-detail', kwargs=kwargs)
            except NoReverseMatch:
                return "/%s/" % language

    def get_active(self):
        return all([
            self.is_active,
            self.publication_start is None or self.publication_start <= now(),
            self.publication_end is None or self.publication_end > now()
        ])

    def get_notification_emails(self):
        return self.category.get_notification_emails()


class JobApplication(models.Model):
    MALE = 'male'
    FEMALE = 'female'

    SALUTATION_CHOICES = (
        (MALE, _('Mr.')),
        (FEMALE, _('Mrs.')),
    )

    job_offer = models.ForeignKey(JobOffer)
    salutation = models.CharField(
        verbose_name=_('Salutation'),
        max_length=20,
        blank=True,
        choices=SALUTATION_CHOICES,
        default=MALE
    )
    first_name = models.CharField(verbose_name=_('First name'), max_length=20)
    last_name = models.CharField(verbose_name=_('Last name'), max_length=20)
    email = models.EmailField(verbose_name=_('E-mail'))
    cover_letter = models.TextField(verbose_name=_('Cover letter'), blank=True)
    created = models.DateTimeField(auto_now_add=True)
    is_rejected = models.BooleanField(_('Rejected'), default=False)
    rejection_date = models.DateTimeField(_('Rejection date'), null=True, blank=True)

    class Meta:
        ordering = ['-created']

    def __unicode__(self):
        return self.get_full_name()

    def get_full_name(self):
        full_name = u' '.join([self.first_name, self.last_name])
        return full_name.strip()


@receiver(pre_delete, sender=JobApplication)
def cleanup_attachments(sender, instance, **kwargs):
    for attachment in instance.attachments.all():
        if attachment:
            attachment.file.delete(False)


class JobApplicationAttachment(models.Model):
    application = models.ForeignKey(JobApplication, related_name='attachments')
    file = JobApplicationFileField()


class JobListPlugin(CMSPlugin):
    def job_offers(self):
        return JobOffer.active.all()
