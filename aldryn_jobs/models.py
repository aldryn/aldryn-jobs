# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import reversion

from django import get_version
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.http import Http404
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.importlib import import_module
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from djangocms_text_ckeditor.fields import HTMLField

from aldryn_reversion.core import version_controlled_content
from aldryn_apphooks_config.managers.parler import (
    AppHookConfigTranslatableManager
)

from cms.models import CMSPlugin
from cms.models.fields import PlaceholderField
from cms.utils.i18n import force_language
from distutils.version import StrictVersion
from emailit.api import send_mail
from functools import partial
from os.path import join as join_path
from parler.models import TranslatableModel, TranslatedFields
from reversion.revisions import RegistrationError
from sortedm2m.fields import SortedManyToManyField
from uuid import uuid4

from .cms_appconfig import JobsConfig
from .managers import NewsletterSignupManager, JobOpeningsManager
from .utils import get_valid_filename

strict_version = StrictVersion(get_version())


def get_user_model_for_fields():
    if strict_version < StrictVersion('1.7.0'):
        return get_user_model()
    else:
        return getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

# We should check if user model is registered, since we're following on that
# relation for EventCoordinator model, if not - register it to
# avoid RegistrationError when registering models that refer to it.
user_model = get_user_model_for_fields()

if strict_version < StrictVersion('1.7.0'):
    # Prior to 1.7 it is pretty straight forward
    revision_manager = reversion.default_revision_manager
    if user_model not in revision_manager.get_registered_models():
        reversion.register(user_model)
else:
    # otherwise it is a pain, but thanks to solution of getting model from
    # https://github.com/django-oscar/django-oscar/commit/c479a1983f326a9b059e157f85c32d06a35728dd  # NOQA
    # we can do almost the same thing from the different side.
    from django.apps import apps
    from django.apps.config import MODELS_MODULE_NAME
    from django.core.exceptions import AppRegistryNotReady

    def get_model(app_label, model_name):
        """
        Fetches a Django model using the app registry.
        This doesn't require that an app with the given app label exists,
        which makes it safe to call when the registry is being populated.
        All other methods to access models might raise an exception about the
        registry not being ready yet.
        Raises LookupError if model isn't found.
        """
        try:
            return apps.get_model(app_label, model_name)
        except AppRegistryNotReady:
            if apps.apps_ready and not apps.models_ready:
                # If this function is called while `apps.populate()` is
                # loading models, ensure that the module that defines the
                # target model has been imported and try looking the model up
                # in the app registry. This effectively emulates
                # `from path.to.app.models import Model` where we use
                # `Model = get_model('app', 'Model')` instead.
                app_config = apps.get_app_config(app_label)
                # `app_config.import_models()` cannot be used here because it
                # would interfere with `apps.populate()`.
                import_module('%s.%s' % (app_config.name, MODELS_MODULE_NAME))
                # In order to account for case-insensitivity of model_name,
                # look up the model through a private API of the app registry.
                return apps.get_registered_model(app_label, model_name)
            else:
                # This must be a different case (e.g. the model really doesn't
                # exist). We just re-raise the exception.
                raise

    # now get the real user model
    model_app_name, model_model = user_model.split('.')
    user_model_object = get_model(model_app_name, model_model)
    # and try to register, if we have a registration error - that means that
    # it has been registered already
    try:
        reversion.register(user_model_object)
    except RegistrationError:
        pass


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


@version_controlled_content(follow=['supervisors', 'app_config'])
@python_2_unicode_compatible
class JobCategory(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(_('Name'), max_length=255),
        slug=models.SlugField(_('Slug'), max_length=255, blank=True,
            help_text=_('Auto-generated. Used in the URL. If changed, the URL'
                        ' will change. Clean it to have it re-created.')),
        meta={'unique_together': [['slug', 'language_code']]}
    )

    supervisors = models.ManyToManyField(
        get_user_model_for_fields(), verbose_name=_('Supervisors'),
        # FIXME: This is mis-named should be "job_categories"?
        related_name='job_opening_categories',
        help_text=_('Those people will be notified via e-mail when new '
                    'application arrives.'),
        blank=True
    )
    app_config = models.ForeignKey(JobsConfig,
        verbose_name=_('app_config'), null=True)

    ordering = models.IntegerField(_('Ordering'), default=0)

    objects = AppHookConfigTranslatableManager()

    class Meta:
        verbose_name = _('Job category')
        verbose_name_plural = _('Job categories')
        ordering = ['ordering']

    def __str__(self):
        return self.safe_translation_getter('name', str(self.pk))

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


@version_controlled_content(follow=['category'])
@python_2_unicode_compatible
class JobOpening(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(_('Title'), max_length=255),
        slug=models.SlugField(_('Slug'), max_length=255, blank=True,
            help_text=_('Auto-generated. Used in the URL. If changed, the URL '
                        'will change. Clean it to have it re-created.')),
        lead_in=HTMLField(_('Lead in'), blank=True,
            help_text=_('Will be displayed in lists')),
        meta={'unique_together': [['slug', 'language_code']]}
    )

    content = PlaceholderField('Job Opening Content')
    category = models.ForeignKey(JobCategory, verbose_name=_('Category'),
        related_name='jobs')
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(_('Active'), default=True)
    publication_start = models.DateTimeField(_('Published since'),
        null=True, blank=True)
    publication_end = models.DateTimeField(_('Published until'),
        null=True, blank=True)
    can_apply = models.BooleanField(_('Viewer can apply for the job'),
        default=True)

    objects = JobOpeningsManager()

    class Meta:
        verbose_name = _('Job opening')
        verbose_name_plural = _('Job openings')
        ordering = ['category__ordering', 'category', '-created']

    def __str__(self):
        return self.safe_translation_getter('title', str(self.pk))

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


@version_controlled_content(follow=['job_opening'])
@python_2_unicode_compatible
class JobApplication(models.Model):
    # FIXME: Gender is not the same as salutation.
    MALE = 'male'
    FEMALE = 'female'

    SALUTATION_CHOICES = (
        (MALE, _('Mr.')),
        (FEMALE, _('Mrs.')),
    )

    job_opening = models.ForeignKey(JobOpening)
    salutation = models.CharField(_('Salutation'),
        max_length=20, blank=True, choices=SALUTATION_CHOICES, default=MALE)
    first_name = models.CharField(_('First name'), max_length=20)
    last_name = models.CharField(_('Last name'), max_length=20)
    email = models.EmailField(_('E-mail'))
    cover_letter = models.TextField(_('Cover letter'), blank=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    is_rejected = models.BooleanField(_('rejected?'), default=False)
    rejection_date = models.DateTimeField(_('rejection date'),
        null=True, blank=True)

    class Meta:
        ordering = ['-created']

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


@version_controlled_content(follow=['application'])
class JobApplicationAttachment(models.Model):
    application = models.ForeignKey(JobApplication, related_name='attachments')
    file = JobApplicationFileField()


@version_controlled_content
@python_2_unicode_compatible
class NewsletterSignup(models.Model):
    recipient = models.EmailField(_('recipient'), unique=True)
    default_language = models.CharField(_('language'), blank=True,
        default='', max_length=32, choices=settings.LANGUAGES)
    signup_date = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    confirmation_key = models.CharField(max_length=40, unique=True)

    app_config = models.ForeignKey(JobsConfig, verbose_name=_('app_config'),
        null=True)

    objects = NewsletterSignupManager()

    def get_absolute_url(self):
        kwargs = {'key': self.confirmation_key}
        with force_language(self.default_language):
            try:
                url = reverse(
                    '{0}:confirm_newsletter_email'.format(
                        self.app_config.namespace),
                    kwargs=kwargs
                )
            except NoReverseMatch:
                try:
                    url = reverse(
                        '{0}:confirm_newsletter_not_found'.format(
                            self.app_config.namespace))
                except NoReverseMatch:
                    raise Http404()
        return url

    def reset_confirmation(self):
        """ Reset the confirmation key.

        Note that the old key won't work anymore
        """
        update_fields = ['confirmation_key', ]
        self.confirmation_key = NewsletterSignup.objects.generate_random_key()
        # check if user was in the mailing list but then disabled newsletter
        # and now wants to get it again
        if self.is_verified and self.is_disabled:
            self.is_disabled = False
            self.is_verified = False
            update_fields.extend(['is_disabled', 'is_verified'])
        self.save(update_fields=update_fields)
        self.send_newsletter_confirmation_email()

    def send_newsletter_confirmation_email(self, request=None):
        context = {
            'data': self,
            'full_name': None,
        }
        # check if we have a user somewhere
        user = None
        if hasattr(self, 'user'):
            user = self.user
        elif request is not None and request.user.is_authenticated():
            user = request.user
        elif self.related_user.filter(signup__pk=self.pk):
            user = self.related_user.filter(signup__pk=self.pk).get()

        if user:
            context['full_name'] = user.get_full_name()

        # get site domain
        full_link = '{0}{1}'.format(
            get_current_site(request).domain,
            self.get_absolute_url()
        )
        context['link'] = self.get_absolute_url()
        context['full_link'] = full_link
        # build url
        send_mail(recipients=[self.recipient],
                  context=context,
                  language=self.default_language,
                  template_base='aldryn_jobs/emails/newsletter_confirmation')

    def confirm(self):
        """
        Confirms NewsletterSignup, excepts that is_verified is checked before
        calling this method.
        """
        self.is_verified = True
        self.save(update_fields=['is_verified', ])

    def disable(self):
        self.is_disabled = True
        self.save(update_fields=['is_disabled', ])

    def __str__(self):
        return '{0} / {1}'.format(self.recipient, self.app_config)


@version_controlled_content(follow=['signup', 'user'])
@python_2_unicode_compatible
class NewsletterSignupUser(models.Model):
    signup = models.ForeignKey(NewsletterSignup, related_name='related_user')
    user = models.ForeignKey(get_user_model_for_fields(),
        related_name='newsletter_signup')

    def get_full_name(self):
        return self.user.get_full_name()

    def __str__(self):
        return 'link to user {0}'.format(self.get_full_name())


class BaseJobsPlugin(CMSPlugin):
    app_config = models.ForeignKey(JobsConfig, verbose_name=_('app_config'),
        null=True, help_text=_(
            'Select appropriate add-on configuration for this plugin.'))

    class Meta:
        abstract = True


@python_2_unicode_compatible
class JobListPlugin(BaseJobsPlugin):
    """ Store job list for JobListPlugin. """
    jobopenings = SortedManyToManyField(JobOpening, blank=True, null=True,
        help_text=_("Select Job Openings to show or don't select any to show "
                    "last job openings. Note that Job Openings form different "
                    "app config would be ignored."))

    def job_openings(self, namespace):
        """
        Return the selected JobOpening for JobListPlugin.

        If no JobOpening are selected, return all active events for namespace
        and language.
        """
        if self.jobopenings.exists():
            return self.jobopenings.filter(
                category__app_config__namespace=namespace).active()

        return (
            JobOpening.objects.filter(category__app_config=self.app_config)
                              .language(self.language)
                              .translated(self.language)
                              .active()
        )

    def __str__(self):
        return force_text(self.pk)

    def copy_relations(self, oldinstance):
        self.jobopenings = oldinstance.jobopenings.all()


class JobCategoriesPlugin(BaseJobsPlugin):

    def __str__(self):
        return _('%s categories') % (self.app_config.get_app_title(), )

    @property
    def categories(self):
        return (
            JobCategory.objects
                       .namespace(self.app_config.namespace)
                       .filter(jobs=True)
                       .annotate(count=models.Count('jobs'))
                       .order_by('ordering', '-count', 'translations__name')
        )


class JobNewsletterRegistrationPlugin(BaseJobsPlugin):
    mail_to_group = models.ManyToManyField(
        Group, verbose_name=_('Notification to'),
        blank=True,
        help_text=_('If user successfuly completed registration.<br/>'
            'Notification would be sent to users from selected groups<br/>'
            'Leave blank to disable notifications.<br/>'))

    def copy_relations(self, oldinstance):
        self.mail_to_group = oldinstance.mail_to_group.all()
