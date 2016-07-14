from datetime import timedelta

from django.utils.translation import override
from django.utils.timezone import now

from cms import api

from ..models import JobCategory, JobsConfig, JobOpening

from .base import JobsBaseTestCase


class TestAppConfigPluginsMixin(object):
    plugin_to_test = 'TextPlugin'
    plugin_params = {}

    def setUp(self):
        super(TestAppConfigPluginsMixin, self).setUp()
        self.plugin_page = self.create_plugin_page()
        self.placeholder = self.plugin_page.placeholders.all()[0]

    def create_plugin_page(self):
        page = api.create_page(
            title="Jobs plugin page en",
            template=self.template,
            language=self.language,
            parent=self.root_page,
            published=True)
        api.create_title('de', 'Jobs plugin page de', page,
                         slug='jobs-plugin-page-de')
        page.publish('en')
        page.publish('de')
        return page.reload()

    def _create_plugin(self, page, language, app_config, **plugin_params):
        """
        Create plugin of type self.plugin_to_test and plugin_params in
        given language to a page placeholder.
        Assumes that page has that translation.
        """
        placeholder = page.placeholders.all()[0]
        plugin = api.add_plugin(
            placeholder, self.plugin_to_test, language,
            app_config=app_config, **plugin_params)
        page.publish(language)
        return plugin


class TestPluginFailuresWithDeletedAppHookMixin(object):
    """
    General test cases for 500 errors if app config or page wtih app hook
    was deleted.
    Relies on setUp which should prepare all plugins
    """

    def test_plugin_doesnt_break_page_if_configured_apphook_was_deleted(self):
        # delete apphooked page
        self.page.delete()

        for language_code in ('en', 'de'):
            with override(language_code):
                page_url_en = self.plugin_page.get_absolute_url()
            response = self.client.get(page_url_en)
            self.assertEqual(response.status_code, 200)

    def test_plugin_doesnt_break_page_for_su_if_apphook_was_deleted(self):
        # delete apphooked page
        self.page.delete()

        for language_code in ('en', 'de'):
            with override(language_code):
                page_url_en = '{0}?edit'.format(
                    self.plugin_page.get_absolute_url())

            login_result = self.client.login(
                username=self.super_user, password=self.super_user_password)
            self.assertEqual(login_result, True)

            response = self.client.get(page_url_en)
            self.assertEqual(response.status_code, 200)

    def test_plugin_does_not_breaks_page_if_job_config_was_deleted(self):
        # delete JobConfig
        self.app_config.delete()

        for language_code in ('en', 'de'):
            with override(language_code):
                page_url_en = self.plugin_page.get_absolute_url()
            response = self.client.get(page_url_en)
            self.assertEqual(response.status_code, 200)

    def test_plugin_doesnt_breaks_page_for_su_if_job_config_was_deleted(self):
        # delete JobConfig
        self.app_config.delete()

        for language_code in ('en', 'de'):
            with override(language_code):
                page_url_en = '{0}?edit'.format(
                    self.plugin_page.get_absolute_url())

            login_result = self.client.login(
                username=self.super_user, password=self.super_user_password)
            self.assertEqual(login_result, True)

            response = self.client.get(page_url_en)
            self.assertEqual(response.status_code, 200)

    def test_plugin_does_not_displays_error_message_to_non_super_users(self):
        # delete apphooked page
        self.page.delete()

        with override('en'):
            page_url = self.plugin_page.get_absolute_url()

        response = self.client.get(page_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            'There is an error in plugin configuration: selected Job')

    def test_plugin_displays_error_message_to_super_users(self):
        # delete apphooked page
        self.page.delete()

        with override('en'):
            page_url = self.plugin_page.get_absolute_url()

        login_result = self.client.login(
            username=self.super_user, password=self.super_user_password)
        self.assertEqual(login_result, True)

        response = self.client.get(page_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'There is an error in plugin configuration: selected Job')


class TestJobCategoriesListPlugin(TestAppConfigPluginsMixin,
                                  TestPluginFailuresWithDeletedAppHookMixin,
                                  JobsBaseTestCase):
    plugin_to_test = 'JobCategoriesList'

    def setUp(self):
        super(TestJobCategoriesListPlugin, self).setUp()
        self.plugin_en = self.create_plugin(
            self.plugin_page, 'en', self.app_config)

        with override('en'):
            self.another_category = JobCategory.objects.create(
                name='Another category',
                app_config=self.app_config)
            self.empty_category = JobCategory.objects.create(
                name='Empty category',
                app_config=self.app_config)

    def create_plugin(self, page, language, app_config,
                      **plugin_params):
        plugin = self._create_plugin(
            page, language, app_config, **plugin_params)
        return plugin

    def test_categories_list_plugin_counters(self):
        """Test JobCategory plugin job openings count"""

        with override('en'):
            JobOpening.objects.create(
                title='job active',
                category=self.default_category)
            JobOpening.objects.create(
                title='job inactive',
                is_active=False,
                category=self.default_category)
            JobOpening.objects.create(
                title='job future',
                publication_start=now() + timedelta(days=1),
                category=self.default_category)
            JobOpening.objects.create(
                title='job past',
                publication_start=now() - timedelta(days=2),
                publication_end=now() - timedelta(days=1),
                category=self.default_category)
            JobOpening.objects.create(
                title='job in another category',
                category=self.another_category)
            page_url = self.plugin_page.get_absolute_url()

        response = self.client.get(page_url)

        self.assertContains(response, self.default_category.name)
        self.assertContains(response, self.another_category.name)
        self.assertNotContains(response, self.empty_category.name)

        self.assertEquals(self.default_category.count(), 1)
        self.assertEquals(self.another_category.count(), 1)
        self.assertEquals(self.empty_category.count(), 0)


class TestJobListPlugin(TestAppConfigPluginsMixin,
                        TestPluginFailuresWithDeletedAppHookMixin,
                        JobsBaseTestCase):
    plugin_to_test = 'JobList'

    def setUp(self):
        super(TestJobListPlugin, self).setUp()
        self.job_opening = self.create_default_job_opening(translated=True)
        self.plugin_en = self.create_plugin(self.plugin_page, 'en',
            self.app_config, jobopenings=self.job_opening)
        self.plugin_de = self.create_plugin(self.plugin_page, 'de',
            self.app_config, jobopenings=self.job_opening)

    def create_plugin(self, page, language, app_config, jobopenings=None,
                      **plugin_params):
        plugin = self._create_plugin(
            page, language, app_config, **plugin_params)
        if jobopenings is not None:
            # we need to update plugin configuration model with correct group
            # it is located under it's own manager
            plugin.aldryn_jobs_joblistplugin.jobopenings.add(
                jobopenings)
            plugin.save()
        return plugin

    def test_list_plugin_shows_selected_items(self):
        # since we setting up plugin in a setUp method with default
        # job opening and default config, at this point it should
        # contain all that we need.
        with override('en'):
            page_url = self.plugin_page.get_absolute_url()
            default_opening_url = self.job_opening.get_absolute_url()
        response = self.client.get(page_url)
        self.assertContains(response, self.job_opening.title)
        self.assertContains(response, default_opening_url)

    def test_list_plugin_doesnt_shows_delayed_openings(self):
        new_opening = self.create_new_job_opening(
            self.prepare_data(1, update_date=True))
        self.plugin_en.aldryn_jobs_joblistplugin.jobopenings.add(new_opening)
        self.plugin_en.save()
        self.plugin_page.publish('en')
        with override('en'):
            page_url = self.plugin_page.get_absolute_url()
            opening_url = new_opening.get_absolute_url()
            default_opening_url = self.job_opening.get_absolute_url()
        response = self.client.get(page_url)
        self.assertNotContains(response, new_opening.title)
        self.assertNotContains(response, opening_url)

        # test that default job opening is still present
        self.assertContains(response, self.job_opening.title)
        self.assertContains(response, default_opening_url)

    def test_list_plugin_doesnt_shows_job_openings_from_other_config(self):
        new_config = JobsConfig.objects.create(namespace='different_namespace')
        # prepare apphook
        self.create_page(
            title='new apphook', slug='new-apphook',
            namespace=new_config.namespace)
        new_category = JobCategory.objects.create(
            name='Completely different namespace',
            slug='completely-different-namespace',
            app_config=new_config)
        new_opening = self.create_new_job_opening(
            self.prepare_data(1, category=new_category))
        self.plugin_en.aldryn_jobs_joblistplugin.jobopenings.add(new_opening)
        self.plugin_en.app_config = new_config
        self.plugin_en.save()
        self.plugin_page.publish('en')
        with override('en'):
            page_url = self.plugin_page.get_absolute_url()
            default_opening_url = self.job_opening.get_absolute_url()
            new_opening_url = new_opening.get_absolute_url()
        response = self.client.get(page_url)
        # check that app config is repsected by plugin
        self.assertContains(response, new_opening.title)
        self.assertContains(response, new_opening_url)
        # check that there is no openings from other config
        self.assertNotContains(response, self.job_opening.title)
        self.assertNotContains(response, default_opening_url)
