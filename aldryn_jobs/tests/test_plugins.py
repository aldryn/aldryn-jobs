from copy import deepcopy

from django.utils.translation import override
from django.contrib.auth.models import Group
from cms import api

from ..models import JobOffer, JobCategory, JobsConfig

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
        api.add_plugin(
            placeholder, self.plugin_to_test, language,
            app_config=app_config, **plugin_params)
        plugin = placeholder.get_plugins().filter(
            language=language)[0].get_plugin_instance()[0]
        plugin.save()
        page.publish(self.language)
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


class TestNewsletterPlugin(TestAppConfigPluginsMixin,
                           TestPluginFailuresWithDeletedAppHookMixin,
                           JobsBaseTestCase):
    plugin_to_test = 'JobNewsletter'

    def setUp(self):
        super(TestNewsletterPlugin, self).setUp()
        self.default_group = Group.objects.get_or_create(
            name='Newsletter signup notifications')[0]
        # create default plugins to test against them
        self.create_plugin(
            page=self.plugin_page,
            language=self.language,
            app_config=self.app_config,
            mail_to_group=self.default_group,
            **self.plugin_params)
        #
        self.create_plugin(self.plugin_page, 'de', self.app_config,
                           mail_to_group=self.default_group)

    def create_plugin(self, page, language, app_config, mail_to_group=None,
                      **plugin_params):
        plugin = self._create_plugin(
            page, language, app_config, **plugin_params)
        if mail_to_group is not None:
            # we need to update plugin configuration model with correct group
            # it is located under it's own manager
            plugin.jobnewsletterregistrationplugin.mail_to_group.add(
                mail_to_group)
            plugin.save()
        return plugin

    # FIXME: should be changed after switch to app_config settings
    # for mailing etc.
    def test_newsletter_plugins_configured_with_different_groups(self):
        other_group = Group.objects.get_or_create(
            name='Newsletter signup notifications DE')[0]
        other_group_plugin = self.create_plugin(
            self.plugin_page, 'de', self.app_config,
            mail_to_group=other_group)
        placeholder = self.plugin_page.placeholders.all()[0]

        # test en plugin group equals to default_group
        plugin = placeholder.get_plugins().filter(language='en')[0]
        self.assertEqual(
            plugin.jobnewsletterregistrationplugin.mail_to_group.count(), 1)
        self.assertEqual(
            plugin.jobnewsletterregistrationplugin.mail_to_group.all()[0],
            self.default_group)

        # test de plugin group
        plugin = placeholder.get_plugins().filter(
            language='de').get(pk=other_group_plugin.pk)
        self.assertEqual(
            plugin.jobnewsletterregistrationplugin.mail_to_group.count(), 2)
        self.assertIn(
            other_group,
            plugin.jobnewsletterregistrationplugin.mail_to_group.all())

    def test_plugin_with_different_groups_does_not_breaks_page(self):
        other_group = Group.objects.get_or_create(
            name='Newsletter signup notifications DE')[0]
        self.create_plugin(
            self.plugin_page, 'de', self.app_config, mail_to_group=other_group)

        for language_code in ('en', 'de'):
            with override(language_code):
                page_url_en = self.plugin_page.get_absolute_url()
            response = self.client.get(page_url_en)
            self.assertEqual(response.status_code, 200)

    def test_plugin_with_deleted_group_does_not_breaks_page(self):
        self.default_group.delete()

        for language_code in ('en', 'de'):
            with override(language_code):
                page_url_en = self.plugin_page.get_absolute_url()
            response = self.client.get(page_url_en)
            self.assertEqual(response.status_code, 200)


class TestJobCategoriesListPlugin(TestAppConfigPluginsMixin,
                                  TestPluginFailuresWithDeletedAppHookMixin,
                                  JobsBaseTestCase):
    plugin_to_test = 'JobCategoriesList'

    def setUp(self):
        super(TestJobCategoriesListPlugin, self).setUp()
        # create plugin for both languages
        self.create_plugin(self.plugin_page, 'en', self.app_config)
        self.create_plugin(self.plugin_page, 'de', self.app_config)

    def create_plugin(self, page, language, app_config,
                      **plugin_params):
        plugin = self._create_plugin(
            page, language, app_config, **plugin_params)
        return plugin


class TestJobListPlugin(TestAppConfigPluginsMixin,
                        TestPluginFailuresWithDeletedAppHookMixin,
                        JobsBaseTestCase):
    plugin_to_test = 'JobList'

    def setUp(self):
        super(TestJobListPlugin, self).setUp()
        job_opening = self.create_default_job_opening(translated=True)
        self.create_plugin(self.plugin_page, 'en', self.app_config,
                           jobopenings=job_opening)
        self.create_plugin(self.plugin_page, 'de', self.app_config,
                           jobopenings=job_opening)

    def create_plugin(self, page, language, app_config, jobopenings=None,
                      **plugin_params):
        plugin = self._create_plugin(
            page, language, app_config, **plugin_params)
        if jobopenings is not None:
            # we need to update plugin configuration model with correct group
            # it is located under it's own manager
            plugin.joblistplugin.jobopenings.add(
                jobopenings)
            plugin.save()
        return plugin

    def create_new_job_opening(self, data):
        with override('en'):
            job_opening = JobOffer.objects.create(**data)
        return job_opening

    def prepare_data(self, replace_with=1, category=None, update_date=False):
        values = deepcopy(self.offer_values_raw['en'])
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

    def test_list_plugin_shows_selected_items(self):
        # since we setting up plugin in a setUp method with default
        # job opening and default config, at this point it should
        # contain all that we need.
        with override('en'):
            page_url = self.plugin_page.get_absolute_url()
            default_opening_url = self.job_offer.get_absolute_url()
        response = self.client.get(page_url)
        self.assertContains(response, self.job_offer.title)
        self.assertContains(response, default_opening_url)

    def test_list_plugin_doesnt_shows_delayed_offers(self):
        new_opening = self.create_new_job_opening(
            self.prepare_data(1, update_date=True))
        self.plugin_en.joblistplugin.joboffers.add(new_opening)
        self.plugin_en.save()
        self.plugin_page.publish('en')
        with override('en'):
            page_url = self.plugin_page.get_absolute_url()
            opening_url = new_opening.get_absolute_url()
            default_opening_url = self.job_offer.get_absolute_url()
        response = self.client.get(page_url)
        self.assertNotContains(response, new_opening.title)
        self.assertNotContains(response, opening_url)

        # test that default job opening is still present
        self.assertContains(response, self.job_offer.title)
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
        self.plugin_en.joblistplugin.joboffers.add(new_opening)
        self.plugin_en.app_config = new_config
        self.plugin_en.save()
        self.plugin_page.publish('en')
        with override('en'):
            page_url = self.plugin_page.get_absolute_url()
            default_opening_url = self.job_offer.get_absolute_url()
            new_opening_url = new_opening.get_absolute_url()
        response = self.client.get(page_url)
        # check that app config is repsected by plugin
        self.assertContains(response, new_opening.title)
        self.assertContains(response, new_opening_url)
        # check that there is no openings from other config
        self.assertNotContains(response, self.job_offer.title)
        self.assertNotContains(response, default_opening_url)
