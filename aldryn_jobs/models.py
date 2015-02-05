# -*- coding: utf-8 -*-

from functools import partial
from os.path import join as join_path
from uuid import uuid4

from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.sites.models import get_current_site
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from cms.models import CMSPlugin
from cms.utils.i18n import force_language, get_current_language
from cms.models.fields import PlaceholderField
from djangocms_text_ckeditor.fields import HTMLField
from emailit.api import send_mail
from hvad.models import TranslatableModel, TranslatedFields, TranslationManager
from hvad.utils import get_translation

from .managers import NewsletterSignupManager


try:
    from django.contrib.auth import get_user_model
except ImportError:  # django < 1.5
    from django.contrib.auth.models import User
else:
    User = get_user_model()

from .utils import get_valid_filename


def default_jobs_attachment_upload_to(instance, filename):
    date = now().strftime('%Y/%m')
    return join_path('attachments', date, str(uuid4()),
                     get_valid_filename(filename))


jobs_attachment_upload_to = getattr(settings,
                                    'ALDRYN_JOBS_ATTACHMENT_UPLOAD_DIR',
                                    default_jobs_attachment_upload_to)

jobs_attachment_storage = getattr(settings,
                                  'ALDRYN_JOBS_ATTACHMENT_STORAGE',
                                  None)

JobApplicationFileField = partial(
    models.FileField,
    max_length=200,
    blank=True,
    null=True,
    upload_to=jobs_attachment_upload_to,
    storage=jobs_attachment_storage
)


def get_slug_in_language(record, language):
    cached_translation_language = record.safe_translation_getter(
        'language_code')

    if language == cached_translation_language:
        # no need to hit db, use cache
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
                              help_text=_(
                                  'Auto-generated. Used in the URL. If '
                                  'changed, the URL will change. '
                                  'Clean it to have it re-created.')),
        meta={'unique_together': [['slug', 'language_code']]}
    )

    supervisors = models.ManyToManyField(User, verbose_name=_('Supervisors'),
                                         related_name='job_offer_categories',
                                         help_text=_(
                                             'Those people will be notified '
                                             'via e-mail when '
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
            try:
                if not slug:
                    return reverse('job-offer-list')
                kwargs = {'category_slug': slug}
                return reverse('category-job-offer-list', kwargs=kwargs)
            except NoReverseMatch:
                return "/%s/" % language

    def get_notification_emails(self):
        return self.supervisors.values_list('email', flat=True)


class ActiveJobOffersManager(TranslationManager):
    def apply_custom_filters(self, qs):
        """
        This is provided as a separate method because hvad's using_translations
        does not call get_query_set.
        """
        qs = qs.filter(is_active=True)
        qs = qs.filter(models.Q(publication_start__isnull=True) | models.Q(
            publication_start__lte=now()))
        qs = qs.filter(models.Q(publication_end__isnull=True) | models.Q(
            publication_end__gt=now()))
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
        qs = super(ActiveJobOffersManager, self)._make_queryset(klass,
                                                                core_filters)
        import hvad

        if hvad.VERSION >= (0, 5, 0):
            return self.apply_custom_filters(qs)
        return qs


class JobOffer(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255),
        slug=models.SlugField(_('Slug'), max_length=255, blank=True,
                              help_text=_(
                                  'Auto-generated. Used in the URL. If '
                                  'changed, the URL will change. '
                                  'Clean it to have it re-created.')),
        lead_in=HTMLField(_('Lead in'), blank=True,
                          help_text=_('Will be displayed in lists')),
        meta={'unique_together': [['slug', 'language_code']]}
    )

    content = PlaceholderField('Job Offer Content')
    category = models.ForeignKey(JobCategory, verbose_name=_('Category'),
                                 related_name='jobs')
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(_('Active'), default=True)
    publication_start = models.DateTimeField(_('Published since'), null=True,
                                             blank=True)
    publication_end = models.DateTimeField(_('Published until'), null=True,
                                           blank=True)
    can_apply = models.BooleanField(_('Viewer can apply for the job'),
                                    default=True)

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
            try:
                if not slug:
                    return self.category.get_absolute_url(language=language)
                kwargs = {
                    'category_slug': get_slug_in_language(self.category,
                                                          language),
                    'job_offer_slug': slug,
                }
                return reverse('job-offer-detail', kwargs=kwargs)
            except NoReverseMatch:
                return "/%s/" % language

    def get_active(self):
        return all([self.is_active,
                    self.publication_start is None or self.publication_start <= now(),
                    self.publication_end is None or self.publication_end > now()])

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
    rejection_date = models.DateTimeField(_('Rejection date'), null=True,
                                          blank=True)

    class Meta:
        ordering = ['-created']

    def __unicode__(self):
        return u'%(first_name)s %(last_name)s' % self.__dict__


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


class JobNewsletterRegistrationPlugin(CMSPlugin):
    def get_form(self):
        from .forms import NewsletterSignupForm
        return NewsletterSignupForm()

class NewsletterSignup(models.Model):
    recipient = models.EmailField(_('Recipient'), unique=True)
    default_language = models.CharField(_('Language'), blank=True,
                                        default='', max_length=32,
                                        choices=settings.LANGUAGES)
    signup_date = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    confirmation_key = models.CharField(max_length=40)  # unique=True

    objects = NewsletterSignupManager()

    def get_absolute_url(self):
        kwargs = {'key': self.confirmation_key}
        with force_language(self.default_language):
            try:
                return reverse('confirm_newsletter_email', kwargs=kwargs)
            except NoReverseMatch:
                return reverse('confirm_newsletter_not_found')

    def reset_confirmation(self):
        """ Reset the confirmation key.

        Note that the old key won't work anymore
        """
        self.confirmation_key = self.objects.generate_random_key()
        self.save(update_fields=['confirmation_key', ])
        self.send_confirmation_email()

    def send_newsletter_confirmation_email(self, request=None):
        context = {'data': self}
        if hasattr(self, 'user'):
            context['first_name'] = self.user.first_name
            context['last_name'] = self.user.last_name
        # get site domain
        context['link'] = '{0}{1}'.format(get_current_site(request).domain,
                                          self.get_absolute_url())
        # build url
        send_mail(recipients=[self.recipient],
                  context=context,
                  template_base='aldryn_jobs/emails/newsletter_confirmation')

    def confirm(self):
        """
        Confirms NewsletterSignup, excepts that is_verified is checked before calling this method.
        """
        self.is_verified = True
        self.save()




