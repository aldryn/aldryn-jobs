# -*- coding: utf-8 -*-
import reversion
from reversion.revisions import RegistrationError
from importlib import import_module

from django import get_version
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.utils.encoding import force_text
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from djangocms_text_ckeditor.fields import HTMLField

from aldryn_reversion.core import version_controlled_content
from aldryn_apphooks_config.models import AppHookConfig
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
from sortedm2m.fields import SortedManyToManyField
from uuid import uuid4

from .managers import NewsletterSignupManager, JobOffersManager
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
    # https://github.com/django-oscar/django-oscar/commit/c479a1983f326a9b059e157f85c32d06a35728dd
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

@version_controlled_content
class JobsConfig(AppHookConfig):
    pass

@version_controlled_content(follow=['supervisors', 'app_config'])
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
    app_config = models.ForeignKey(
        JobsConfig, verbose_name=_('app_config'), null=True
    )

    ordering = models.IntegerField(_('Ordering'), default=0)

    objects = AppHookConfigTranslatableManager()

    class Meta:
        verbose_name = _('Job category')
        verbose_name_plural = _('Job categories')
        ordering = ['ordering']

    def __unicode__(self):
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
                    return reverse('{0}:job-offer-list'.format(namespace))
                kwargs = {'category_slug': slug}
                return reverse(
                    '{0}:category-job-offer-list'.format(namespace),
                    kwargs=kwargs,
                    current_app=self.app_config.namespace
                )
            except NoReverseMatch:
                return "/%s/" % language

    def get_notification_emails(self):
        return self.supervisors.values_list('email', flat=True)

@version_controlled_content(follow=['category', 'app_config'])
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
    app_config = models.ForeignKey(
        JobsConfig, verbose_name=_('app_config'), null=True
    )

    objects = JobOffersManager()

    class Meta:
        verbose_name = _('Job offer')
        verbose_name_plural = _('Job offers')
        ordering = ['category__ordering', 'category', '-created']

    def __unicode__(self):
        return self.safe_translation_getter('title', str(self.pk))

    def get_absolute_url(self, language=None):
        language = language or self.get_current_language()
        slug = self.safe_translation_getter('slug', language_code=language)
        category_slug = self.category.safe_translation_getter(
            'slug', language_code=language
        )
        if self.app_config_id:
            namespace = self.app_config.namespace
        else:
            namespace = 'aldryn_jobs'
        with force_language(language):
            try:
                # FIXME: does not looks correct return category url here
                if not slug:
                    return self.category.get_absolute_url(language=language)
                kwargs = {
                    'category_slug': category_slug,
                    'job_offer_slug': slug,
                }
                return reverse(
                    '{0}:job-offer-detail'.format(namespace),
                    kwargs=kwargs,
                    current_app=self.app_config.namespace
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

@version_controlled_content(follow=['job_offer', 'app_config'])
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

    app_config = models.ForeignKey(JobsConfig, verbose_name=_('app_config'), null=True)

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

@version_controlled_content(follow=['application'])
class JobApplicationAttachment(models.Model):
    application = models.ForeignKey(JobApplication, related_name='attachments')
    file = JobApplicationFileField()

@version_controlled_content
class NewsletterSignup(models.Model):
    recipient = models.EmailField(_('Recipient'), unique=True)
    default_language = models.CharField(_('Language'), blank=True,
                                        default='', max_length=32,
                                        choices=settings.LANGUAGES)
    signup_date = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    confirmation_key = models.CharField(max_length=40, unique=True)

    objects = NewsletterSignupManager()

    def get_absolute_url(self):
        kwargs = {'key': self.confirmation_key}
        with force_language(self.default_language):
            try:
                return reverse('aldryn_jobs:confirm_newsletter_email', kwargs=kwargs)
            except NoReverseMatch:
                return reverse('aldryn_jobs:confirm_newsletter_not_found')

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
        full_link = '{0}{1}'.format(get_current_site(request).domain,
                                          self.get_absolute_url())
        context['link'] = self.get_absolute_url()
        context['full_link'] = full_link
        # build url
        send_mail(recipients=[self.recipient],
                  context=context,
                  template_base='aldryn_jobs/emails/newsletter_confirmation')

    def confirm(self):
        """
        Confirms NewsletterSignup, excepts that is_verified is checked before calling this method.
        """
        self.is_verified = True
        self.save(update_fields=['is_verified', ])

    def disable(self):
        self.is_disabled = True
        self.save(update_fields=['is_disabled', ])

    def __unicode__(self):
        return unicode(self.recipient)

@version_controlled_content(follow=['signup', 'user'])
class NewsletterSignupUser(models.Model):
    signup = models.ForeignKey(NewsletterSignup, related_name='related_user')
    user = models.ForeignKey(
        get_user_model_for_fields(), related_name='newsletter_signup'
    )

    def get_full_name(self):
        return self.user.get_full_name()

    def __unicode__(self):
        return unicode('link to user {0} '.format(self.get_full_name()))


class BaseJobsPlugin(CMSPlugin):
    app_config = models.ForeignKey(
        JobsConfig, verbose_name=_('app_config'), null=True
    )

    class Meta:
        abstract = True


class JobListPlugin(BaseJobsPlugin):

    """ Store job list for JobListPlugin. """

    joboffers = SortedManyToManyField(
        JobOffer, blank=True, null=True,
        help_text=_("Select Job Offers to show or don't select any to show "
                    "last job offers.")
        )

    def job_offers(self):
        """
        Return the selected JobOffer for JobListPlugin.

        If no JobOffer are selected, return all active events for namespace
        and language.
        """
        if self.joboffers.exists():
            return self.joboffers.all()

        namespace = self.app_config and self.app_config.namespace
        return (
            JobOffer.objects.namespace(namespace)
                            .language(self.language)
                            .translated(self.language)
                            .active()
        )

    def __unicode__(self):
        return force_text(self.pk)

    def copy_relations(self, oldinstance):
        self.joboffers = oldinstance.joboffers.all()


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


class JobNewsletterRegistrationPlugin(CMSPlugin):
    # NOTE: does not need app_config in this one
    # TODO: add configurable parameters for registration form plugin
    mail_to_group = models.ManyToManyField(
        Group, verbose_name=_('Signup notification to')
    )

    def copy_relations(self, oldinstance):
        self.mail_to_group = oldinstance.mail_to_group.all()
