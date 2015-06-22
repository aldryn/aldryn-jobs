from django.utils.translation import override
from django.contrib.auth.models import Group
from cms import api

from .base import JobsBaseTestCase
from ..models import JobsConfig


class TestAppConfigPluginsBase(JobsBaseTestCase):
    plugin_to_test = 'TextPlugin'
    plugin_params = {}

    def setUp(self):
        super(TestAppConfigPluginsBase, self).setUp()
        self.plugin_page = self.create_plugin_page()
        self.placeholder = self.plugin_page.placeholders.all()[0]

    def create_plugin_page(self):
        page = api.create_page(
            title="Jobs plugin page en", template=self.template, language=self.language,
            parent=self.root_page, published=True)
        api.create_title('de', 'Jobs plugin page de', page, slug='jobs-plugin-page-de')
        page.publish('en')
        page.publish('de')
        return page.reload()

    def create_plugin(self, page, language, app_config, **plugin_params):
        """
        Create plugin of type self.plugin_to_test and plugin_params in given language
        to a page placeholder.
        Assumes that page has that translation.
        """
        placeholder = page.placeholders.all()[0]
        api.add_plugin(
            placeholder, self.plugin_to_test, language,
            app_config=app_config, **plugin_params)
        plugin = placeholder.get_plugins().filter(language=language)[0].get_plugin_instance()[0]
        plugin.save()
        page.publish(self.language)
        return plugin


class TestNewsletterPlugin(TestAppConfigPluginsBase):
    plugin_to_test = 'JobNewsletter'

    def setUp(self):
        super(TestNewsletterPlugin, self).setUp()
        self.default_group = Group.objects.get_or_create(name='Newsletter signup notifications')[0]
        self.create_plugin(
            page=self.plugin_page,
            language=self.language,
            app_config=self.app_config,
            mail_to_group=self.default_group,
            **self.plugin_params)

    def create_plugin(self, page, language, app_config, mail_to_group=None, **plugin_params):
        plugin = super(TestNewsletterPlugin, self).create_plugin(
            page, language, app_config, **plugin_params)
        if mail_to_group is not None:
            # we need to update plugin configuration model with correct group
            # it is located under it's own manager
            plugin.jobnewsletterregistrationplugin.mail_to_group.add(mail_to_group)
            plugin.save()
        return plugin

    def test_newsletter_plugins_does_not_breaks_page(self):
        with override(self.language):
            page_url = self.plugin_page.get_absolute_url()
        response = self.client.get(page_url)
        self.assertEqual(response.status_code, 200)

    def test_newsletter_plugins_does_not_break_page_on_other_language(self):
        other_group = Group.objects.get_or_create(name='Newsletter signup notifications DE')[0]
        self.create_plugin(self.plugin_page, 'de', self.app_config, mail_to_group=other_group)
        with override('de'):
            page_url = self.plugin_page.get_absolute_url()
        response = self.client.get(page_url)
        self.assertEqual(response.status_code, 200)

    def tets_newsletter_plugins_configured_with_different_groups(self):
        other_group = Group.objects.get_or_create(name='Newsletter signup notifications DE')[0]
        self.create_plugin(self.plugin_page, 'de', self.app_config, mail_to_group=other_group)
        placeholder = self.plugin_page.placeholders.all()[0]

        # test en plugin group equals to default_group
        plugin = placeholder.get_plugins().filter(language='en')[0]
        self.assertEqual(plugin.mail_to_group, self.plugin_params['mail_to_group'])

        # test de plugin group
        plugin = placeholder.get_plugins().filter(language='de')[0]
        self.assertEqual(plugin.mail_to_group, other_group)
