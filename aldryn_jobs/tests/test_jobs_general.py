from django.conf import settings
from django.core.urlresolvers import reverse

from django.utils.translation import override
from parler.utils.context import switch_language

from cms import api
from cms.models import Placeholder
from cms.utils import get_cms_setting
from cms.utils.i18n import force_language
from cms.test_utils.testcases import CMSTestCase

from ..models import JobCategory, JobOpening
from ..cms_appconfig import JobsConfig
from ..utils import namespace_is_apphooked

from .base import JobsBaseTestCase, tz_datetime


class JobsAddTest(JobsBaseTestCase):

    def test_create_job_category(self):
        """
        Check if We can create a new job category.
        """
        category_name = 'Administration'
        new_category = JobCategory.objects.create(name=category_name)
        self.assertEqual(new_category.name, 'Administration')
        self.assertEqual(JobCategory.objects.filter(
            pk=new_category.pk).count(), 1)
        self.assertEqual(
            JobCategory.objects.get(pk=new_category.pk).name, category_name)

    def test_create_job_opening(self):
        """
        Check if We can create a new job opening.
        """
        title = 'Programmer'
        opening = JobOpening.objects.create(
            title=title, category=self.default_category)
        self.assertEqual(opening.title, title)
        self.assertEqual(JobOpening.objects.all()[0], opening)

    def test_category_relation_to_job_opening(self):
        """
        Check if We can access a job opening through a category.
        """
        title = 'Senior'
        opening = JobOpening.objects.create(
            title=title, category=self.default_category)
        self.assertIn(opening, self.default_category.jobs.all())

    def test_add_opening_list_plugin_api(self):
        """
        We add an opening to the Plugin and look it up
        """
        title = 'Manager'
        JobOpening.objects.create(title=title, category=self.default_category)
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

    def get_i18n_urls_for_job(self, job_opening):
        job_urls = []
        for language, _ in settings.LANGUAGES:
            with switch_language(job_opening, language):
                job_url = job_opening.get_absolute_url()
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
        self.create_default_job_opening(translated=True)

        for apphook_url in self.apphook_urls:
            response = self.client.get(apphook_url)
            self.assertEqual(response.status_code, 200)

    def test_apphooked_pages_are_available_for_super_user(self):
        """
        Test apphooked pages are available if there is jobs and categories for
        super user
        """
        self.create_default_job_opening(translated=True)

        login_result = self.client.login(
            username=self.super_user, password=self.super_user_password)
        self.assertEqual(login_result, True)

        for apphook_url in self.apphook_urls:
            apphook_url_with_toolbar = '{0}?edit'.format(apphook_url)
            response = self.client.get(apphook_url_with_toolbar)
            self.assertEqual(response.status_code, 200)

    def test_job_opening_is_accessible(self):
        job_opening = self.create_default_job_opening(translated=True)
        job_urls = self.get_i18n_urls_for_job(job_opening)

        for job_url in job_urls:
            response = self.client.get(job_url)
            self.assertEqual(response.status_code, 200)

    def test_job_opening_is_accessible_by_super_user(self):
        job_opening = self.create_default_job_opening(translated=True)
        job_urls = self.get_i18n_urls_for_job(job_opening)

        login_result = self.client.login(
            username=self.super_user, password=self.super_user_password)
        self.assertEqual(login_result, True)

        for job_url in job_urls:
            response = self.client.get(job_url)
            self.assertEqual(response.status_code, 200)

    def test_job_opening_list_page_contains_correct_detail_urls(self):
        job_opening = self.create_default_job_opening(translated=True)

        for language, _ in settings.LANGUAGES:
            with switch_language(job_opening, language):
                job_url = job_opening.get_absolute_url()
                job_title = job_opening.title
            with override(language):
                opening_list_url = self.page.get_absolute_url()

            response = self.client.get(opening_list_url)
            self.assertContains(response, job_url)
            self.assertContains(response, job_title)

    def test_jobs_config_placeholders_are_usable(self):
        # make sure default config is apphooked to a page.
        # FIXME: until migrations are not enabled and ensured to work with
        # tests - this won't test the default namespace =(
        # though this test is (or at least it should be) pretty useful.
        default_config = JobsConfig.objects.get_or_create(
            namespace='aldryn_jobs')[0]
        if not namespace_is_apphooked(default_config.namespace):
            page = api.create_page(
                title='default jobs config en', template=self.template,
                language='en',
                published=True,
                parent=self.root_page,
                apphook='JobsApp',
                apphook_namespace=default_config.namespace,
                publication_date=tz_datetime(2014, 6, 8)
            )
            api.create_title('de', 'default jobs config en', page)
            page.publish('en')
            page.publish('de')
            page_with_default_config = page.reload()
            # get some time for aldryn-apphook-reload to perform actions
            with force_language('en'):
                default_config_url = page_with_default_config.get_absolute_url()
            self.client.get(default_config_url)

        configs = JobsConfig.objects.all()
        # this would be used to build unique value for text plugin
        # namespace-lang-placeholder_name, which would be searched on the page.
        plugin_content_raw = '{0}-{1}-{2}'
        plugins_content = {}
        for cfg in configs:
            cfg_placehodlers = [field for field in cfg._meta.fields
                                if field.__class__ == Placeholder]
            placeholders_names = [placeholder.name for placeholder in
                                  cfg_placehodlers]
            # make sure that we have an empty list to store plugins content
            plugins_content[cfg] = []
            for placeholder_name in placeholders_names:
                placeholder_instance = getattr(cfg, placeholder_name)
                self.assertNotEqual(type(placeholder_instance), type(None))
                plugin_text = plugin_content_raw.format(
                    cfg.namespace, 'en', placeholder_name)
                api.add_plugin(
                    placeholder_instance, 'TextPlugin', 'en',
                    body=plugin_text)
                # track other namespaces plugin content to check
                # their uniqueness
                plugins_content[cfg].append(plugin_text)

        # test <config> placeholder content if it is attached to a page
        skipped = []
        for cfg in configs:
            if not namespace_is_apphooked(cfg.namespace):
                skipped.append(cfg)
                continue

            with force_language('en'):
                apphook_url = reverse('{0}:job-opening-list'.format(
                    cfg.namespace))
            response = self.client.get(apphook_url)

            # test own content
            for text in plugins_content[cfg]:
                self.assertIn(response, text)

            # make sure other namespace plugins are not leaked
            other_configs = [config for config in plugins_content.keys()
                             if config is not cfg]
            all_other_namespace_plugins_text = [
                text for other_config in other_configs
                for text in plugins_content[other_config]]
            for other_plugins_text in all_other_namespace_plugins_text:
                self.assertNotIn(response, other_plugins_text)
        # make sure that we tested at least one config
        self.assertNotEqual(configs.count(), len(skipped))

    def test_one_active_hook_page_shows_openings_for_its_config_only(self):
        new_config = JobsConfig.objects.create(
            namespace='another_apphook_not_active')

        default_opening = self.create_default_job_opening()

        # default apphooked page url
        with override('en'):
            page_url = self.page.get_absolute_url()
            new_category = JobCategory.objects.create(
                name='Completely different namespace',
                slug='completely-different-namespace',
                app_config=new_config)
            new_opening = self.create_new_job_opening(
                self.prepare_data(1, category=new_category))
            default_opening_url = default_opening.get_absolute_url()

        response = self.client.get(page_url)
        # check same apphook openings and their links are present
        self.assertContains(response, default_opening_url)
        self.assertContains(response, default_opening.title)
        # check other apphook openings and their links are absent
        # doesn't makes sense to test url for new opening
        # since it cannot be properly resolved because of absent apphook
        self.assertNotContains(response, new_opening.title)

    def test_two_active_hook_page_shows_openings_for_its_config_only(self):
        # prepare apphook
        new_config = JobsConfig.objects.create(
            namespace='another_apphook_not_active')
        new_apphook_page = self.create_page(
            title='new apphook', slug='new-apphook',
            namespace=new_config.namespace)
        default_opening = self.create_default_job_opening()

        # default apphooked page url
        with override('en'):
            default_page_url = self.page.get_absolute_url()
            new_apphook_page_url = new_apphook_page.get_absolute_url()
            # create new category and opening
            new_category = JobCategory.objects.create(
                name='Completely different namespace',
                slug='completely-different-namespace',
                app_config=new_config)
            new_opening = self.create_new_job_opening(
                self.prepare_data(1, category=new_category))
            # prepare openings links
            new_opening_url = new_opening.get_absolute_url()
            default_opening_url = default_opening.get_absolute_url()

        # test default page
        response = self.client.get(default_page_url)
        # check same apphook openings and their links are present
        self.assertContains(response, default_opening_url)
        self.assertContains(response, default_opening.title)
        # check other apphook openings and their links are absent
        self.assertNotContains(response, new_opening_url)
        self.assertNotContains(response, new_opening.title)

        # test page with new apphook
        response = self.client.get(new_apphook_page_url)
        # check same apphook openings and their links are present
        self.assertContains(response, new_opening_url)
        self.assertContains(response, new_opening.title)
        # check other apphook openings and their links are absent
        self.assertNotContains(response, default_opening_url)
        self.assertNotContains(response, default_opening.title)

    def test_two_active_hook_pages_same_category_and_opening_names(self):
        # regression for issue with two job configs (different namespace)
        # which have same categories names/slugs and same openings title/slugs
        new_config = JobsConfig.objects.create(
            namespace='another_apphook_to_test')
        new_apphook_page = self.create_page(
            title='new apphook', slug='new-apphook',
            namespace=new_config.namespace)

        default_opening = self.create_default_job_opening(translated=True)

        same_name_category = self.create_default_job_category(
            translated=True, config=new_config)
        same_name_opening = self.create_default_job_opening(
            translated=True, category=same_name_category)

        lead_in_text_raw = '{0} lead in for other config'

        for language in ('de', 'en'):
            # get urls
            default_opening_url = default_opening.get_absolute_url(language)
            same_name_opening_url = same_name_opening.get_absolute_url(language)

            with override(language):
                default_app_url = self.page.get_absolute_url()
                other_app_url = new_apphook_page.get_absolute_url()
            with switch_language(same_name_opening, language):
                # change lead in to be different for other opening
                same_name_opening.lead_in = lead_in_text_raw.format(
                    language)
                same_name_opening.save()

            # urls should be different because namespace is different
            self.assertNotEqual(default_app_url, other_app_url)

            response_default = self.client.get(default_app_url)
            self.assertEqual(response_default.status_code, 200)
            self.assertContains(response_default, default_opening_url)

            response_other = self.client.get(other_app_url)
            self.assertEqual(response_other.status_code, 200)
            self.assertContains(response_other, same_name_opening_url)

            # test translated content, unfortunately we need to explicitly
            # switch language
            with switch_language(default_opening, language):
                self.assertContains(response_default, default_opening.title)
            with switch_language(same_name_opening, language):
                self.assertContains(response_other, same_name_opening.title)

    def test_detail_view_same_category_and_opening_names(self):
        # regression for issue with two job configs (different namespace)
        # which have same categories names/slugs and same openings title/slugs
        new_config = JobsConfig.objects.create(
            namespace='another_apphook_to_test')
        self.create_page(
            title='new apphook', slug='new-apphook',
            namespace=new_config.namespace)

        default_opening = self.create_default_job_opening(translated=True)

        same_name_category = self.create_default_job_category(
            translated=True, config=new_config)
        same_name_opening = self.create_default_job_opening(
            translated=True, category=same_name_category)

        lead_in_text_raw = '{0} lead in for other config'

        for language in ('de', 'en'):
            # get urls
            default_opening_url = default_opening.get_absolute_url(language)
            same_name_opening_url = same_name_opening.get_absolute_url(language)
            with switch_language(same_name_opening, language):
                # change lead in to be different for other opening
                same_name_opening.lead_in = lead_in_text_raw.format(
                    language)
                same_name_opening.save()

            # urls should be different because namespace is different
            self.assertNotEqual(default_opening_url, same_name_opening_url)

            # default one
            response_default = self.client.get(default_opening_url)
            self.assertEqual(response_default.status_code, 200)
            # same named
            response_other = self.client.get(same_name_opening_url)
            self.assertEqual(response_other.status_code, 200)
            # test translatable content
            with switch_language(default_opening, language):
                self.assertContains(response_default, default_opening.title)
                self.assertContains(response_default, default_opening.lead_in)
            with switch_language(same_name_opening, language):
                self.assertContains(response_other, same_name_opening.title)
                self.assertContains(response_other, same_name_opening.lead_in)
