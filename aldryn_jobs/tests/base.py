# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime, timedelta
from copy import deepcopy

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.test import TransactionTestCase
from django.utils.timezone import get_current_timezone
from django.utils.translation import override

from cms import api
from cms.utils import get_cms_setting

from ..models import JobsConfig, JobCategory, JobOpening


def tz_datetime(*args, **kwargs):
    """ Return datetime with arguments in UTC timezone """
    return datetime(tzinfo=get_current_timezone(), *args, **kwargs)


class JobsBaseTestCase(TransactionTestCase):

    default_category_values = {
        'en': {
            'name': 'Default category name en',
            'slug': 'default-category-name-en',
        },
        'de': {
            'name': 'Default category name de',
            'slug': 'default-category-name-de',
        },
    }
    default_job_values = {
        'en': {
            'title': 'Default job opening en',
            'slug': 'default-job-opening-en',
            'lead_in': '<p>Default job for default people! <br/>'
                       'Apply now!</p>',
        },
        'de': {
            'title': 'Default job opening de',
            'slug': 'default-job-opening-de',
            'lead_in': '<p>Default job for default people! Now in German! <br/>'
                       'Apply now!</p>',
        },
    }
    default_plugin_content = {
        'en': 'Awesome job details here EN',
        'de': 'Awesome German job details here DE',
    }
    plugin_values_raw = {
        'en': 'English New, revision {0}, content en',
        'de': 'German revision {0}, new content de',
    }
    opening_values_raw = {
        'en': {
            'title': 'Title revision {0} en',
            'slug': 'title-revision-{0}-en',
            'lead_in': '<p>Job revision {0}! EN</p>',
        },
        'de': {
            'title': 'Title revision {0} de',
            'slug': 'title-revision-{0}-de',
            'lead_in': '<p>Job revision {0}! DE</p>',
        },
    }
    category_values_raw = {
        'en': {
            'name': 'Revision {0} category name en',
            'slug': 'revision-{0}-category-name-en',
        },
        'de': {
            'name': 'Revision {0} category name de',
            'slug': 'revision-{0}-category-name-de',
        },
    }
    default_publication_start = {
        'publication_start': datetime.now(tz=get_current_timezone()),
    }
    default_publication_end = {
        'publication_end': datetime.now(
            tz=get_current_timezone()) + timedelta(days=1),
    }
    application_default_values = {
        'first_name': 'Default_first_name',
        'last_name': 'Default_last_name',
        'email': 'example@example.com',
    }
    application_values_raw = {
        'first_name': 'First_name_{0}',
        'last_name': 'Last_name_{0}',
        'email': 'example_{0}@example.com',
    }
    signup_default_values = {
        'recipient': 'initial@example.com',
        'is_verified': False,
        'is_disabled': False,
        'confirmation_key': 'default confirmation key',
    }
    signup_values_raw = {
        'confirmation_key': 'confirmation key {0}{0}{0}',
        'recipient': 'recipient_{0}@example.com'
    }

    def setUp(self):
        super(JobsBaseTestCase, self).setUp()
        self.template = get_cms_setting('TEMPLATES')[0][0]
        self.language = settings.LANGUAGES[0][0]
        self.app_config = JobsConfig.objects.create(
            namespace='jobs_test_namespace'
        )
        self.default_category = self.create_default_job_category(
            translated=True)
        self.root_page = self.create_root_page()
        self.page = self.create_page()

        self.staff_user_password = 'staff_pw'
        self.staff_user = self.create_staff_user(
            'staff', self.staff_user_password)
        self.super_user_password = 'super_pw'
        self.super_user = self.create_super_user(
            'super', self.super_user_password)

    def create_root_page(self):
        root_page = api.create_page(
            'root page', self.template, self.language, published=True)
        api.create_title('de', 'root page de', root_page)
        root_page.publish('en')
        root_page.publish('de')
        return root_page.reload()

    def create_page(self, title=None, slug=None, namespace=None):

        if namespace is None:
            namespace = self.app_config.namespace

        if title is None:
            title = 'Jobs'

        if slug is None:
            slug = 'jobs-app'

        page = api.create_page(
            title='{0} en'.format(title),
            slug='{0}-en'.format(slug),
            template=self.template,
            language=self.language,
            published=True,
            parent=self.root_page,
            apphook='JobsApp',
            apphook_namespace=namespace)
        api.create_title(
            'de', '{0} de'.format(title), page, slug='{0}-de'.format(slug))
        page.publish('en')
        page.publish('de')
        # unfortunately aphook reload doesn't restart server fast,
        # so we do an empty request otherwise tests might
        # fail because it can't get correct url
        with override('en'):
            empty_url = page.get_absolute_url()
        self.client.get(empty_url)
        return page.reload()

    def tearDown(self):
        super(JobsBaseTestCase, self).tearDown()
        app_config = JobsConfig.objects.filter(pk=self.app_config.pk)
        if app_config:
            app_config.get().delete()
        cache.clear()

    def create_user(self, user_name, user_password, is_staff=False,
                    is_superuser=False):
        return User.objects.create(
            username=user_name,
            first_name='{0} first_name'.format(user_name),
            last_name='{0} last_name'.format(user_name),
            password=make_password(user_password),
            is_staff=is_staff,
            is_superuser=is_superuser
        )

    def create_staff_user(self, user_name, user_password):
        staff_user = self.create_user(user_name, user_password, is_staff=True)
        return staff_user

    def create_super_user(self, user_name, user_password):
        super_user = self.create_user(user_name, user_password,
                                      is_superuser=True)
        return super_user

    def create_default_job_category(self, translated=False, config=None):
        # ensure that we always start with english, since it looks
        # like there is some issues with handling active language
        # between tests cases run

        if config is None:
            config = self.app_config

        with override('en'):
            job_category = JobCategory.objects.create(
                app_config=config,
                **self.default_category_values['en'])

        # check if we need a translated job_category
        if translated:
            job_category.create_translation(
                'de', **self.default_category_values['de'])

        return JobCategory.objects.language('en').get(pk=job_category.pk)

    def create_default_job_opening(self, translated=False, category=None):
        # ensure that we always start with english, since it looks
        # like there is some issues with handling active language
        # between tests cases run

        if category is None:
            category = self.default_category

        with override('en'):
            job_opening = JobOpening.objects.create(
                category=category,
                **self.default_job_values['en'])
            api.add_plugin(
                job_opening.content,
                'TextPlugin',
                'en',
                body=self.default_plugin_content['en'])

        # check if we need a translated job opening
        if translated:
            job_opening.create_translation(
                'de', **self.default_job_values['de'])
            with override('de'):
                api.add_plugin(job_opening.content, 'TextPlugin', 'de',
                               body=self.default_plugin_content['de'])

        return JobOpening.objects.language('en').get(pk=job_opening.pk)

    def make_new_values(self, values_dict, replace_with):
        """
        Replace formatting symbol {0} with replace_with param.
        modifies dates by + timedelta(days=int(replace_with))
        Returns new dictionary with same keys and replaced symbols.
        """
        new_dict = {}
        for key, value in values_dict.items():
            if key in ('publication_start', 'publication_end'):
                new_val = value + timedelta(days=replace_with)
            else:
                new_val = value.format(replace_with)
            new_dict[key] = new_val
        return new_dict

    def create_new_job_opening(self, data):
        with override('en'):
            job_opening = JobOpening.objects.create(**data)
        return job_opening

    def prepare_data(self, replace_with=1, category=None, update_date=False):
        values = deepcopy(self.opening_values_raw['en'])
        # if we need to change date to something in future
        # we should do it before call to self.make_new_values
        if update_date:
            values.update(self.default_publication_start)
        # make new values adds timedelta days=number which is passed as a
        # second argument
        values = self.make_new_values(values, replace_with)
        # setup category
        if category is None:
            values['category'] = self.default_category
        else:
            values['category'] = category
        # if date was not updated - use the default one
        if not update_date:
            values.update(self.default_publication_start)
        return values
