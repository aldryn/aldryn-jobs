# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from cms.api import add_plugin
from cms.utils import permissions
from cms.utils.conf import get_cms_setting
from cms.wizards.wizard_pool import wizard_pool
from cms.wizards.wizard_base import Wizard
from cms.wizards.forms import BaseFormMixin

from djangocms_text_ckeditor.widgets import TextEditorWidget
from djangocms_text_ckeditor.html import clean_html
from parler.forms import TranslatableModelForm

from .cms_appconfig import JobsConfig
from .models import JobCategory, JobOpening
from .utils import namespace_is_apphooked


class ConfigCheckMixin(object):

    def user_has_add_permission(self, user, **kwargs):
        """
        Return True if the current user has permission to add a JobCategory or
        JobOpening (depending on value of `perm_string` class variable.
        :param user: The current user
        :param kwargs: Ignored here
        :return: True if user has add permission, else False
        """
        # No one can create a job object, if there is no app_config yet.
        configs = JobsConfig.objects.all()
        if not configs or not any([namespace_is_apphooked(config.namespace)
                                   for config in configs]):
            return False
        # Ensure user has permission to create job objects.
        if user.is_superuser or user.has_perm(self.perm_string):
            return True

        # By default, no permission.
        return False


class JobCategoryWizard(ConfigCheckMixin, Wizard):
    perm_string = "aldryn_jobs.add_jobcategory"


class JobOpeningWizard(ConfigCheckMixin, Wizard):
    perm_string = "aldryn_jobs.add_jobopening"

    def user_has_add_permission(self, user, **kwargs):
        """
        Return True if the current user has permission to add a JobOpening and
        there is at least one JobCategory.
        :param user: The current user
        :param kwargs: Ignored here
        :return: True if user has add permission, else False
        """
        base_perm = super(JobOpeningWizard, self).user_has_add_permission(
            user, **kwargs)
        return base_perm and JobCategory.objects.exists()


class CreateJobCategoryForm(BaseFormMixin, TranslatableModelForm):
    """
    The ModelForm for the JobCategory wizard. Note that JobCategory has few
    translated fields that we need to access, so, we use TranslatableModelForm
    """

    class Meta:
        model = JobCategory
        fields = ['name', 'slug', 'app_config']

    def __init__(self, **kwargs):
        super(CreateJobCategoryForm, self).__init__(**kwargs)
        # If there's only 1 app_config, don't bother show the
        # app_config choice field, we'll choose the option for the user.
        app_configs = JobsConfig.objects.all()
        # check if app config is apphooked
        app_configs = [app_config
                       for app_config in app_configs
                       if namespace_is_apphooked(app_config.namespace)]
        if len(app_configs) == 1:
            self.fields['app_config'].widget = forms.HiddenInput()
            self.fields['app_config'].initial = app_configs[0].pk


class CreateJobOpeningForm(BaseFormMixin, TranslatableModelForm):
    """
    The ModelForm for the Job Opening wizard. Note that JobOpening has few
    translated fields that we need to access, so, we use TranslatableModelForm
    """

    job_opening_content = forms.CharField(
        label="Content", required=False, widget=TextEditorWidget,
        help_text=_("Optional. If provided, will be added to the main body of "
                    "the Opening content."),
    )

    class Meta:
        model = JobOpening
        fields = ['title', 'category', 'is_active', 'lead_in',
                  'publication_start', 'publication_end',
                  'job_opening_content', 'can_apply', ]

    def __init__(self, **kwargs):
        super(CreateJobOpeningForm, self).__init__(**kwargs)

        # If there's only 1 category, don't bother show the empty label (choice)
        if JobCategory.objects.count() == 1:
            self.fields['category'].empty_label = None
        self.fields['publication_start'].help_text = _(
            'Date Acceptable Formats: 2015-11-30, 11/30/2015, 11/30/15')
        self.fields['publication_end'].help_text = _(
            'Date Acceptable Formats: 2015-11-30, 11/30/2015, 11/30/15')

    def save(self, commit=True):
        job_opening = super(CreateJobOpeningForm, self).save(commit=False)

        # If 'job_opening_content' field has value, create a TextPlugin with same and add
        # it to the PlaceholderField
        job_opening_content = clean_html(self.cleaned_data.get('job_opening_content', ''), False)

        content_plugin = get_cms_setting('PAGE_WIZARD_CONTENT_PLUGIN')
        content_field = get_cms_setting('PAGE_WIZARD_CONTENT_PLUGIN_BODY')

        if job_opening_content and permissions.has_plugin_permission(
                self.user, content_plugin, 'add'):

            # If the job_opening has not been saved, then there will be no
            # Placeholder set-up for this question yet, so, ensure we have saved
            # first.
            if not job_opening.pk:
                job_opening.save()

            if job_opening and job_opening.content:
                plugin_kwargs = {
                    'placeholder': job_opening.content,
                    'plugin_type': content_plugin,
                    'language': self.language_code,
                    content_field: job_opening_content,
                }
                add_plugin(**plugin_kwargs)

        job_opening.save()

        return job_opening


job_category_wizard = JobCategoryWizard(
    title=_(u"New job category"),
    weight=500,
    form=CreateJobCategoryForm,
    description=_(u"Create a new job category.")
)

wizard_pool.register(job_category_wizard)

job_opening_wizard = JobOpeningWizard(
    title=_(u"New job opening"),
    weight=550,
    form=CreateJobOpeningForm,
    description=_(u"Create a new job opening.")
)

wizard_pool.register(job_opening_wizard)
