# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import get_version
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from djangocms_text_ckeditor.fields import HTMLField
from aldryn_apphooks_config.managers.parler import (
    AppHookConfigTranslatableManager
)
from aldryn_translation_tools.models import (
    TranslationHelperMixin, TranslatedAutoSlugifyMixin,
)

from cms.models import CMSPlugin
from cms.models.fields import PlaceholderField
from cms.utils.i18n import force_language
from distutils.version import LooseVersion
from functools import partial
from os.path import join as join_path
from parler.models import TranslatableModel, TranslatedFields
from sortedm2m.fields import SortedManyToManyField
from uuid import uuid4

from .cms_appconfig import JobsConfig
from .managers import JobOpeningsManager
from .utils import get_valid_filename

# NOTE: We need to use LooseVersion NOT StrictVersion as Aldryn sometimes uses
# patched versions of Django with version numbers in the form: X.Y.Z.postN
loose_version = LooseVersion(get_version())


# We should check if user model is registered, since we're following on that
# relation for EventCoordinator model, if not - register it to
# avoid RegistrationError when registering models that refer to it.
user_model = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


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


@python_2_unicode_compatible
class JobCategory(TranslatedAutoSlugifyMixin,
                  TranslationHelperMixin,
                  TranslatableModel):
    slug_source_field_name = 'name'

    translations = TranslatedFields(
        name=models.CharField(_('name'), max_length=255),
        slug=models.SlugField(
            _('slug'), max_length=255, blank=True,
            help_text=_('Auto-generated. Used in the URL. If changed, the URL '
                        'will change. Clear it to have the slug re-created.'))
    )

    supervisors = models.ManyToManyField(
        getattr(settings, 'AUTH_USER_MODEL', 'auth.User'), verbose_name=_('supervisors'),
        # FIXME: This is mis-named should be "job_categories"?
        related_name='job_opening_categories',
        help_text=_('Supervisors will be notified via email when a new '
                    'job application arrives.'),
        blank=True
    )
    app_config = models.ForeignKey(
        JobsConfig, null=True,
        verbose_name=_('app configuration'), related_name='categories')

    ordering = models.IntegerField(_('ordering'), default=0)

    objects = AppHookConfigTranslatableManager()

    class Meta:
        verbose_name = _('job category')
        verbose_name_plural = _('job categories')
        ordering = ['ordering']

    def __str__(self):
        return self.safe_translation_getter('name', str(self.pk))

    def _slug_exists(self, *args, **kwargs):
        """Provide additional filtering for slug generation"""
        qs = kwargs.get('qs', None)
        if qs is None:
            qs = self._get_slug_queryset()
        # limit qs to current app_config only
        kwargs['qs'] = qs.filter(app_config=self.app_config)
        return super(JobCategory, self)._slug_exists(*args, **kwargs)

    def get_absolute_url(self, language=None):
        language = language or self.get_current_language()
        slug = self.safe_translation_getter('slug', language_code=language)
        if self.app_config_id:
            namespace = self.app_config.namespace
        else:
            namespace = 'aldryn_jobs'
        with force_language(language):
            try:
                if not slug:
                    return reverse('{0}:job-opening-list'.format(namespace))
                kwargs = {'category_slug': slug}
                return reverse(
                    '{0}:category-job-opening-list'.format(namespace),
                    kwargs=kwargs,
                    current_app=self.app_config.namespace
                )
            except NoReverseMatch:
                return "/%s/" % language

    def get_notification_emails(self):
        return self.supervisors.values_list('email', flat=True)

    # We keep this 'count' name for compatibility in templates:
    # there used to be annotate() call with the same property name.
    def count(self):
        return self.jobs.active().count()


@python_2_unicode_compatible
class JobOpening(TranslatedAutoSlugifyMixin,
                 TranslationHelperMixin,
                 TranslatableModel):
    slug_source_field_name = 'title'

    translations = TranslatedFields(
        title=models.CharField(_('title'), max_length=255),
        slug=models.SlugField(
            _('slug'), max_length=255, blank=True,
            unique=False, db_index=False,
            help_text=_('Auto-generated. Used in the URL. If changed, the URL '
                        'will change. Clear it to have the slug re-created.')),
        lead_in=HTMLField(
            _('short description'), blank=True,
            help_text=_('This text will be displayed in lists.'))
    )

    content = PlaceholderField('Job Opening Content')
    category = models.ForeignKey(JobCategory, verbose_name=_('category'), related_name='jobs')
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(_('active?'), default=True)
    publication_start = models.DateTimeField(_('published since'), null=True, blank=True)
    publication_end = models.DateTimeField(_('published until'), null=True, blank=True)
    can_apply = models.BooleanField(_('viewer can apply for the job?'), default=True)

    ordering = models.IntegerField(_('ordering'), default=0)

    objects = JobOpeningsManager()

    class Meta:
        verbose_name = _('job opening')
        verbose_name_plural = _('job openings')
        # DO NOT attempt to add 'translated__title' here.
        ordering = ['ordering', ]

    def __str__(self):
        return self.safe_translation_getter('title', str(self.pk))

    def _slug_exists(self, *args, **kwargs):
        """Provide additional filtering for slug generation"""
        qs = kwargs.get('qs', None)
        if qs is None:
            qs = self._get_slug_queryset()
        # limit qs to current app_config only
        kwargs['qs'] = qs.filter(category__app_config=self.category.app_config)
        return super(JobOpening, self)._slug_exists(*args, **kwargs)

    def get_absolute_url(self, language=None):
        language = language or self.get_current_language()
        slug = self.safe_translation_getter('slug', language_code=language)
        category_slug = self.category.safe_translation_getter(
            'slug', language_code=language
        )
        namespace = getattr(
            self.category.app_config, "namespace", "aldryn_jobs")
        with force_language(language):
            try:
                # FIXME: does not looks correct return category url here
                if not slug:
                    return self.category.get_absolute_url(language=language)
                kwargs = {
                    'category_slug': category_slug,
                    'job_opening_slug': slug,
                }
                return reverse(
                    '{0}:job-opening-detail'.format(namespace),
                    kwargs=kwargs,
                    current_app=self.category.app_config.namespace
                )
            except NoReverseMatch:
                # FIXME: this is wrong, if have some problem in reverse
                #        we should know
                return "/%s/" % language

    def get_active(self):
        return all([
            self.is_active,
            self.publication_start is None or self.publication_start <= now(),
            self.publication_end is None or self.publication_end > now()
        ])

    def get_notification_emails(self):
        return self.category.get_notification_emails()


@python_2_unicode_compatible
class JobApplication(models.Model):
    # FIXME: Gender is not the same as salutation.
    MALE = 'male'
    FEMALE = 'female'

    SALUTATION_CHOICES = (
        (MALE, _('Mr.')),
        (FEMALE, _('Mrs.')),
    )

    job_opening = models.ForeignKey(JobOpening, related_name='applications')
    salutation = models.CharField(_('salutation'), max_length=20, blank=True, choices=SALUTATION_CHOICES, default=MALE)
    first_name = models.CharField(_('first name'), max_length=20)
    last_name = models.CharField(_('last name'), max_length=20)
    email = models.EmailField(_('email'), max_length=254)
    cover_letter = models.TextField(_('cover letter'), blank=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    is_rejected = models.BooleanField(_('rejected?'), default=False)
    rejection_date = models.DateTimeField(_('rejection date'), null=True, blank=True)

    class Meta:
        ordering = ['-created']
        verbose_name = _('job application')
        verbose_name_plural = _('job applications')

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        full_name = ' '.join([self.first_name, self.last_name])
        return full_name.strip()


@receiver(pre_delete, sender=JobApplication)
def cleanup_attachments(sender, instance, **kwargs):
    for attachment in instance.attachments.all():
        if attachment:
            attachment.file.delete(False)


class JobApplicationAttachment(models.Model):
    application = models.ForeignKey(JobApplication, related_name='attachments',
                                    verbose_name=_('job application'))
    file = JobApplicationFileField()


@python_2_unicode_compatible
class JobListPlugin(CMSPlugin):
    """ Store job list for JobListPlugin. """

    cmsplugin_ptr = models.OneToOneField(
        CMSPlugin, related_name='aldryn_jobs_joblistplugin', parent_link=True)

    app_config = models.ForeignKey(
        JobsConfig,
        verbose_name=_('app configuration'), null=True,
        help_text=_('Select appropriate app. configuration for this plugin.'))

    jobopenings = SortedManyToManyField(
        JobOpening, blank=True,
        verbose_name=_('job openings'),
        help_text=_("Choose specific Job Openings to show or leave empty to "
                    "show latest. Note that Job Openings from different "
                    "app configs will not appear."))

    def __str__(self):
        return force_text(self.pk)

    def get_job_openings(self, namespace):
        """
        Return the selected JobOpening for JobListPlugin.

        If no JobOpening are selected, return all active events for namespace
        and language, sorted by title.
        """
        if self.jobopenings.exists():
            return self.jobopenings.namespace(namespace).active()

        return (
            JobOpening.objects.namespace(namespace)
                              .language(self.language)
                              .active_translations(self.language)
                              .active()
        )

    def copy_relations(self, oldinstance):
        self.app_config = oldinstance.app_config
        self.jobopenings = oldinstance.jobopenings.all()


@python_2_unicode_compatible
class JobCategoriesPlugin(CMSPlugin):

    cmsplugin_ptr = models.OneToOneField(
        CMSPlugin, related_name='aldryn_jobs_jobcategoriesplugin',
        parent_link=True)

    app_config = models.ForeignKey(
        JobsConfig,
        verbose_name=_('app configuration'), null=True,
        help_text=_('Select appropriate app. configuration for this plugin.'))

    def __str__(self):
        return _('%s categories') % (self.app_config.namespace,)

    @property
    def categories(self):
        categories_qs = JobCategory.objects.namespace(
            self.app_config.namespace).order_by('ordering')
        return (category for category in categories_qs if category.count())

    def copy_relations(self, oldinstance):
        self.app_config = oldinstance.app_config
