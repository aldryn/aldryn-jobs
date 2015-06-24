# -*- coding: utf-8 -*-
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.utils.translation import override

from cms import api

from .base import JobsBaseTestCase
from .test_plugins import TestAppConfigPluginsMixin
from ..models import JobsConfig, NewsletterSignup, NewsletterSignupUser


class TestNewsletterSignupViews(TestAppConfigPluginsMixin, JobsBaseTestCase):
    plugin_to_test = 'JobNewsletter'

    def setUp(self):
        super(TestNewsletterSignupViews, self).setUp()
        self.default_group = Group.objects.get_or_create(
            name='Newsletter signup notifications')[0]
        self.create_plugin(
            page=self.plugin_page,
            language=self.language,
            app_config=self.app_config,
            mail_to_group=self.default_group,
            **self.plugin_params)

    def test_signup_user_is_created(self):
        with override('en'):
            signup_url = reverse('{0}:register_newsletter'.format(self.app_config.namespace))
        response = self.client.post(
            signup_url,
            {'recipient': 'initial@reicipent.com'},
            follow=True)
        self.assertGreater(len(response.redirect_chain), 0)
        # redirect_chain consists of list of tuples
        # ('/path/', <status_code>) so check only status code
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertContains(
            response, 'Thank you for registration. '
                      'Confirmation letter is sent to your E-mail.')
        self.assertEqual(NewsletterSignup.objects.count(), 1)
        signup = NewsletterSignup.objects.all()[0]
        self.assertEqual(signup.recipient, 'initial@reicipent.com')

    def test_signup_user_created_disabled_and_not_confirmed(self):
        with override('en'):
            signup_url = reverse('{0}:register_newsletter'.format(self.app_config.namespace))
        response = self.client.post(
            signup_url,
            {'recipient': 'initial@reicipent.com'},
            follow=True)
        self.assertEqual(NewsletterSignup.objects.count(), 1)
        signup = NewsletterSignup.objects.all()[0]
        self.assertFalse(signup.is_verified)
        self.assertFalse(signup.is_disabled)

    def test_django_user_is_tracked_correctly_if_logged_in(self):
        test_user = {
            'user_name': 'testuser1',
            'user_password': 'test_pw',
        }
        test_user_object = self.create_user(**test_user)
        with override('en'):
            signup_url = reverse('{0}:register_newsletter'.format(self.app_config.namespace))

        login_result = self.client.login(
            username=test_user['user_name'],
            password=test_user['user_password'])
        self.assertEqual(login_result, True)

        response = self.client.post(
            signup_url,
            {'recipient': 'initial@reicipent.com'},
            follow=True)
        # test that objects were created
        self.assertEqual(NewsletterSignup.objects.count(), 1)
        self.assertEqual(NewsletterSignupUser.objects.count(), 1)

        # test values are correct
        signup = NewsletterSignup.objects.all()[0]
        signup_user = NewsletterSignupUser.objects.all()[0]
        self.assertEqual(signup_user.user, test_user_object)
        self.assertEqual(signup_user.signup, signup)

    def test_language_is_tracked_correctly(self):
        with override('de'):
            signup_url = reverse(
                '{0}:register_newsletter'.format(self.app_config.namespace))
        response = self.client.post(
            signup_url,
            {'recipient': 'initial@reicipent.com'},
            follow=True)
        self.assertEqual(NewsletterSignup.objects.count(), 1)
        signup = NewsletterSignup.objects.all()[0]
        self.assertEqual(signup.default_language, 'de')

        with override('en'):
            signup_url = reverse(
                '{0}:register_newsletter'.format(self.app_config.namespace))
        response = self.client.post(
            signup_url,
            {'recipient': 'different_language@reicipent.com'},
            follow=True)
        self.assertEqual(NewsletterSignup.objects.count(), 2)
        signup = NewsletterSignup.objects.all()[1]
        self.assertEqual(signup.default_language, 'en')

    def test_app_config_is_tracked_correctly(self):
        # setup another apphooked page, since reload takes some time
        # we will setup apphook on the beginning of a test case
        new_config = JobsConfig.objects.create(namespace='new_appconfig')
        self.create_page(
            title='Another apphooked jobs',
            slug='another-apphooked-jobs',
            namespace=new_config.namespace)

        # default app config
        with override('en'):
            signup_url = reverse(
                '{0}:register_newsletter'.format(self.app_config.namespace))
        response = self.client.post(
            signup_url,
            {'recipient': 'initial@reicipent.com'},
            follow=True)
        self.assertEqual(NewsletterSignup.objects.count(), 1)
        signup = NewsletterSignup.objects.all()[0]
        self.assertEqual(signup.app_config, self.app_config)

        # new app config
        with override('en'):
            signup_url = reverse(
                '{0}:register_newsletter'.format(new_config.namespace))
        response = self.client.post(
            signup_url,
            {'recipient': 'different_apphook@reicipent.com'},
            follow=True)
        self.assertEqual(NewsletterSignup.objects.count(), 2)
        signup = NewsletterSignup.objects.all()[1]
        self.assertEqual(signup.app_config, new_config)

    def test_newsletter_confirmation_works(self):
        # default app config
        with override('en'):
            signup_url = reverse(
                '{0}:register_newsletter'.format(self.app_config.namespace))
        response = self.client.post(
            signup_url,
            {'recipient': 'initial@reicipent.com'},
            follow=True)
        self.assertEqual(NewsletterSignup.objects.count(), 1)
        signup = NewsletterSignup.objects.all()[0]

        with override('en'):
            confirmation_link = reverse(
                '{0}:confirm_newsletter_email'.format(
                    self.app_config.namespace),
                kwargs={'key': signup.confirmation_key}
            )
        response = self.client.get(confirmation_link)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'After pushing confirm button you will receive jobs newsletter.')
        # confirm registration
        response = self.client.post(
            confirmation_link,
            {'confirmation_key': signup.confirmation_key},
            follow=True)
        # check success message
        self.assertContains(
            response, 'Your email {0} is confirmed.'.format(signup.recipient))
        # get a fresh signup object
        signup = NewsletterSignup.objects.all()[0]
        self.assertTrue(signup.is_verified)

    def test_confirmation_of_confirmed_signup_raises_404(self):
        pass

    def test_unsubscribe_link_disables_signup(self):
        pass

    def test_confirmation_letter_is_being_sent_to_user(self):
        pass

    def test_send_newsletter_uses_app_config(self):
        pass
