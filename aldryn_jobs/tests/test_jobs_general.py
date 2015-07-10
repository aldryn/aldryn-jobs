from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from django.utils.translation import override
from parler.utils.context import switch_language

from cms import api
from cms.utils import get_cms_setting
from cms.test_utils.testcases import BaseCMSTestCase, CMSTestCase

from ..models import JobCategory, JobOffer

from .base import JobsBaseTestCase


class JobsAddTest(JobsBaseTestCase):

    def test_create_job_category(self):
        """
        Check if We can create a new job category.
        """
        category_name = 'Administration'
        new_category = JobCategory.objects.create(name=category_name,
                                                  app_config=self.app_config)
        self.assertEqual(new_category.name, 'Administration')
        self.assertEqual(JobCategory.objects.filter(
            pk=new_category.pk).count(), 1)
        self.assertEqual(
            JobCategory.objects.get(pk=new_category.pk).name, category_name)

    def test_create_job_offer(self):
        """
        Check if We can create a new job offer.
        """
        title = 'Programmer'
        offer = JobOffer.objects.create(
            title=title, category=self.default_category,
            app_config=self.app_config)
        self.assertEqual(offer.title, title)
        self.assertEqual(JobOffer.objects.all()[0], offer)

    def test_category_relation_to_job_offer(self):
        """
        Check if We can access a job offer through a category.
        """
        title = 'Senior'
        offer = JobOffer.objects.create(
            title=title, category=self.default_category,
            app_config=self.app_config)
        self.assertIn(offer, self.default_category.jobs.all())

    def test_add_offer_list_plugin_api(self):
        """
        We add an offer to the Plugin and look it up
        """
        title = 'Manager'
        JobOffer.objects.create(title=title, category=self.default_category,
                                app_config=self.app_config)
        placeholder = self.page.placeholders.all()[0]
        api.add_plugin(placeholder, 'JobList', self.language)
        self.page.publish(self.language)
        with override(self.language):
            url = self.page.get_absolute_url()
        response = self.client.get(url)
        self.assertContains(response, title)


class JobsGeneralTests(CMSTestCase):

    def setUp(self):
        # prepare root page
        self.template = get_cms_setting('TEMPLATES')[0][0]
        self.language = settings.LANGUAGES[0][0]
        self.root_page = api.create_page(
            'root page', self.template, self.language, published=True)

        # create translations for all languages
        for language, _ in settings.LANGUAGES[1:]:
            api.create_title(
                language, self.root_page.get_slug(), self.root_page)
            self.root_page.publish(language)

    def test_response_code_if_no_jobs_apphooks_created(self):
        # If is no apphooks for aldryn-jobs check that cms still works
        for language, _ in settings.LANGUAGES:
            with override(language):
                root_url = self.root_page.get_absolute_url()
                response = self.client.get(root_url)
                self.assertEqual(response.status_code, 200)


class JobApphookTest(JobsBaseTestCase):

    def setUp(self):
        super(JobApphookTest, self).setUp()
        self.root_page_urls = self.get_root_page_urls()
        self.apphook_urls = self.get_apphook_urls()

    def get_root_page_urls(self):
        """
        get root page urls for all languages.
        """
        root_page_urls = []
        for language, _ in settings.LANGUAGES:
            root_page_url = self.root_page.get_absolute_url()
            root_page_urls.append(root_page_url)
        return root_page_urls

    def get_apphook_urls(self):
        # use to track apphooked urls, should be different for each language
        # at least because of language code
        apphook_urls = []
        # populate apphook_urls with root page url so that we would be sure
        # that url doesn't leads us to a root page of website.

        for language, _ in settings.LANGUAGES:
            with override(language):
                apphook_url = self.page.get_absolute_url()
                self.assertNotIn(apphook_url, self.root_page_urls)
                apphook_urls.append(apphook_url)
        return apphook_urls

    def get_i18n_urls_for_job(self, job_offer):
        job_urls = []
        for language, _ in settings.LANGUAGES:
            with switch_language(job_offer, language):
                job_url = job_offer.get_absolute_url()
                self.assertNotIn(job_url, job_urls)
                job_urls.append(job_url)
        return job_urls

    def test_app_hooked_page_is_available_on_all_languages(self):
        for apphook_url in self.apphook_urls:
            response = self.client.get(apphook_url)
            self.assertEqual(response.status_code, 200)

    def test_apphooked_pages_are_available_for_super_users(self):
        login_result = self.client.login(
            username=self.super_user, password=self.super_user_password)
        self.assertEqual(login_result, True)

        for apphook_url in self.apphook_urls:
            apphook_url_with_toolbar = '{0}?edit'.format(apphook_url)
            response = self.client.get(apphook_url_with_toolbar)
            self.assertEqual(response.status_code, 200)

    def test_apphooked_pages_are_available_for_jobs_and_categories(self):
        self.create_default_job_offer(translated=True)

        for apphook_url in self.apphook_urls:
            response = self.client.get(apphook_url)
            self.assertEqual(response.status_code, 200)

    def test_apphooked_pages_are_available_for_super_user(self):
        """
        Test apphooked pages are available if there is jobs and categories for
        super user
        """
        self.create_default_job_offer(translated=True)

        login_result = self.client.login(
            username=self.super_user, password=self.super_user_password)
        self.assertEqual(login_result, True)

        for apphook_url in self.apphook_urls:
            apphook_url_with_toolbar = '{0}?edit'.format(apphook_url)
            response = self.client.get(apphook_url_with_toolbar)
            self.assertEqual(response.status_code, 200)

    def test_job_offer_is_accessible(self):
        job_offer = self.create_default_job_offer(translated=True)
        job_urls = self.get_i18n_urls_for_job(job_offer)

        for job_url in job_urls:
            response = self.client.get(job_url)
            self.assertEqual(response.status_code, 200)

    def test_job_offer_is_accessible_by_super_user(self):
        job_offer = self.create_default_job_offer(translated=True)
        job_urls = self.get_i18n_urls_for_job(job_offer)

        login_result = self.client.login(
            username=self.super_user, password=self.super_user_password)
        self.assertEqual(login_result, True)

        for job_url in job_urls:
            response = self.client.get(job_url)
            self.assertEqual(response.status_code, 200)

    def test_job_offer_list_page_contains_correct_detail_urls(self):
        job_offer = self.create_default_job_offer(translated=True)

        for language, _ in settings.LANGUAGES:
            with switch_language(job_offer, language):
                job_url = job_offer.get_absolute_url()
                job_title = job_offer.title
            with override(language):
                offer_list_url = self.page.get_absolute_url()

            response = self.client.get(offer_list_url)
            self.assertContains(response, job_url)
            self.assertContains(response, job_title)
