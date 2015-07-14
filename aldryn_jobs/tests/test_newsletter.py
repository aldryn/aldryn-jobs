# -*- coding: utf-8 -*-
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.utils.translation import override

from .base import JobsBaseTestCase
from .test_plugins import TestAppConfigPluginsMixin
from ..models import (JobsConfig, JobOpening, JobCategory, NewsletterSignup,
    NewsletterSignupUser)


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

    def test_signup_user_is_created(self):
        with override('en'):
            signup_url = reverse('{0}:register_newsletter'.format(
                self.app_config.namespace))
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
            signup_url = reverse('{0}:register_newsletter'.format(
                self.app_config.namespace))
        self.client.post(
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
            signup_url = reverse('{0}:register_newsletter'.format(
                self.app_config.namespace))

        login_result = self.client.login(
            username=test_user['user_name'],
            password=test_user['user_password'])
        self.assertEqual(login_result, True)

        self.client.post(
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
        self.client.post(
            signup_url,
            {'recipient': 'initial@reicipent.com'},
            follow=True)
        self.assertEqual(NewsletterSignup.objects.count(), 1)
        signup = NewsletterSignup.objects.all()[0]
        self.assertEqual(signup.default_language, 'de')

        with override('en'):
            signup_url = reverse(
                '{0}:register_newsletter'.format(self.app_config.namespace))
        self.client.post(
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
        self.client.post(
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
        self.client.post(
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
        signup = NewsletterSignup.objects.create(
            recipient='initial@reicipent.com',
            is_verified=True,
            default_language='en',
            app_config=self.app_config,
            confirmation_key=NewsletterSignup.objects.generate_random_key())

        with override('en'):
            confirmation_link = reverse(
                '{0}:confirm_newsletter_email'.format(
                    self.app_config.namespace),
                kwargs={'key': signup.confirmation_key}
            )
        response = self.client.get(confirmation_link)
        self.assertEqual(response.status_code, 404)

    def test_confirmation_of_confirmed_signup_raises_404_post(self):
        signup = NewsletterSignup.objects.create(
            recipient='initial@reicipent.com',
            is_verified=True,
            default_language='en',
            app_config=self.app_config,
            confirmation_key=NewsletterSignup.objects.generate_random_key())

        with override('en'):
            confirmation_link = reverse(
                '{0}:confirm_newsletter_email'.format(
                    self.app_config.namespace),
                kwargs={'key': signup.confirmation_key}
            )
        response = self.client.post(
            confirmation_link, {'confirmation_key': signup.confirmation_key})
        signup = NewsletterSignup.objects.get(pk=signup.pk)
        self.assertFalse(signup.is_disabled)
        self.assertEqual(response.status_code, 404)

    def test_unsubscribe_link_disables_signup(self):
        signup = NewsletterSignup.objects.create(
            recipient='initial@reicipent.com',
            is_verified=True,
            default_language='en',
            app_config=self.app_config,
            confirmation_key=NewsletterSignup.objects.generate_random_key())

        with override('en'):
            unsubscribe_link = reverse(
                '{0}:unsubscribe_from_newsletter'.format(
                    self.app_config.namespace),
                kwargs={'key': signup.confirmation_key}
            )
        # test get
        response = self.client.get(unsubscribe_link)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unsubscribe from newsletter')
        # test post
        response = self.client.post(
            unsubscribe_link, {'confirmation_key': signup.confirmation_key})
        signup = NewsletterSignup.objects.get(pk=signup.pk)
        self.assertTrue(signup.is_verified)
        self.assertTrue(signup.is_disabled)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'You will no longer receive jobs newsletter.')

    def test_unsubscribe_of_disabled_signup_raises_404(self):
        signup = NewsletterSignup.objects.create(
            recipient='initial@reicipent.com',
            is_verified=True,
            is_disabled=True,
            default_language='en',
            app_config=self.app_config,
            confirmation_key=NewsletterSignup.objects.generate_random_key())

        with override('en'):
            unsubscribe_link = reverse(
                '{0}:unsubscribe_from_newsletter'.format(
                    self.app_config.namespace),
                kwargs={'key': signup.confirmation_key}
            )
        response = self.client.get(unsubscribe_link)
        self.assertEqual(response.status_code, 404)

    def test_unsubscribe_of_disabled_signup_raises_404_post(self):
        signup = NewsletterSignup.objects.create(
            recipient='initial@reicipent.com',
            is_verified=True,
            is_disabled=True,
            default_language='en',
            app_config=self.app_config,
            confirmation_key=NewsletterSignup.objects.generate_random_key())

        with override('en'):
            unsubscribe_link = reverse(
                '{0}:unsubscribe_from_newsletter'.format(
                    self.app_config.namespace),
                kwargs={'key': signup.confirmation_key}
            )
        response = self.client.post(
            unsubscribe_link, {'confirmation_key': signup.confirmation_key})
        signup = NewsletterSignup.objects.get(pk=signup.pk)
        self.assertTrue(signup.is_disabled)
        self.assertEqual(response.status_code, 404)

    def test_unsubscribe_of_not_verified_signup_raises_404_post(self):
        signup = NewsletterSignup.objects.create(
            recipient='initial@reicipent.com',
            default_language='en',
            app_config=self.app_config,
            confirmation_key=NewsletterSignup.objects.generate_random_key())

        with override('en'):
            unsubscribe_link = reverse(
                '{0}:unsubscribe_from_newsletter'.format(
                    self.app_config.namespace),
                kwargs={'key': signup.confirmation_key}
            )
        response = self.client.post(
            unsubscribe_link, {'confirmation_key': signup.confirmation_key})
        signup = NewsletterSignup.objects.get(pk=signup.pk)
        self.assertFalse(signup.is_disabled)
        self.assertFalse(signup.is_verified)
        self.assertEqual(response.status_code, 404)

    def test_confirmation_letter_is_being_sent_to_user(self):
        with override('en'):
            signup_url = reverse(
                '{0}:register_newsletter'.format(self.app_config.namespace))
        self.client.post(
            signup_url,
            {'recipient': 'initial@reicipent.com'},
            follow=True)

        self.assertEqual(NewsletterSignup.objects.count(), 1)
        signup = NewsletterSignup.objects.all()[0]
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        self.assertEqual(email.to[0], signup.recipient)
        self.assertEqual(len(email.recipients()), 1)

        with override(signup.default_language):
            confirmation_link = reverse(
                '{0}:confirm_newsletter_email'.format(
                    self.app_config.namespace),
                kwargs={'key': signup.confirmation_key})

        self.assertNotEqual(email.body.find(confirmation_link), -1)

    def test_notification_letter_is_being_sent_admin_user(self):
        # prepare staff user
        self.staff_user.email = 'staff@email.com'
        self.staff_user.groups.add(self.default_group)
        self.staff_user.save()
        # settings for whom to notify are taken from plugin settings and
        # settings files, so to have something - we should create a plugin
        # it should be on published page (after creation, which is done inside
        # of self.create_plugin
        self.create_plugin(
            page=self.plugin_page,
            language=self.language,
            app_config=self.app_config,
            mail_to_group=self.default_group,
            **self.plugin_params)
        # prepare user
        signup = NewsletterSignup.objects.create(
            recipient='initial@reicipent.com',
            default_language='en',
            app_config=self.app_config,
            confirmation_key=NewsletterSignup.objects.generate_random_key())
        with override(signup.default_language):
            confirmation_link = reverse(
                '{0}:confirm_newsletter_email'.format(
                    self.app_config.namespace),
                kwargs={'key': signup.confirmation_key})
        self.client.post(
            confirmation_link, {'confirmation_key': signup.confirmation_key})
        signup = NewsletterSignup.objects.get(pk=signup.pk)
        self.assertTrue(signup.is_verified)
        self.assertGreater(len(mail.outbox), 0)
        email = mail.outbox[0]
        self.assertIn(
            self.staff_user.email, [out_mail.to[0] for out_mail in mail.outbox])
        self.assertEqual(len(email.recipients()), 1)
        notification_message = (
            'New recipient "{0}" is added to job '
            'newsletter mailing list.'.format(signup.recipient))
        self.assertNotEqual(email.body.find(notification_message), -1)

    def test_notification_is_using_settings_from_settings_py(self):
        # prepare user
        signup = NewsletterSignup.objects.create(
            recipient='initial@reicipent.com',
            default_language='en',
            app_config=self.app_config,
            confirmation_key=NewsletterSignup.objects.generate_random_key())
        with override(signup.default_language):
            confirmation_link = reverse(
                '{0}:confirm_newsletter_email'.format(
                    self.app_config.namespace),
                kwargs={'key': signup.confirmation_key})
        self.client.post(
            confirmation_link, {'confirmation_key': signup.confirmation_key})
        signup = NewsletterSignup.objects.get(pk=signup.pk)
        self.assertTrue(signup.is_verified)
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        self.assertEqual(email.to[0], 'default_admin@notification.em')
        self.assertEqual(len(email.recipients()), 1)

    def test_send_newsletter_uses_app_config(self):
        # newsletter should distinguish between apphooks, and
        # should not send newsletter to recipients if they have
        # different app_config then job opening.

        # setup another apphooked page, since reload takes some time
        # we will setup apphook on the beginning of a test case
        new_config = JobsConfig.objects.create(namespace='new_appconfig')
        self.create_page(
            title='Another apphooked jobs',
            slug='another-apphooked-jobs',
            namespace=new_config.namespace)

        signup_default_namespace = NewsletterSignup.objects.create(
            recipient='initial@reicipent.com',
            is_verified=True,
            default_language='en',
            app_config=self.app_config,
            confirmation_key=NewsletterSignup.objects.generate_random_key())

        signup_new_namespace = NewsletterSignup.objects.create(
            recipient='new@reicipent.com',
            is_verified=True,
            default_language='en',
            app_config=new_config,
            confirmation_key=NewsletterSignup.objects.generate_random_key())

        opening_default = self.create_default_job_opening(translated=True)
        with override('en'):
            category_new_config = JobCategory.objects.create(
                app_config=new_config,
                **self.make_new_values(self.category_values_raw['en'], 1)
            )
            opening_new_config = JobOpening.objects.create(
                category=category_new_config,
                **self.make_new_values(self.opening_values_raw['en'], 1)
            )

        # send newsletter
        NewsletterSignup.objects.send_job_notifiation(
            job_list=[job.pk for job in (opening_default, opening_new_config)])

        self.assertEqual(len(mail.outbox), 2)
        email0 = mail.outbox[0]
        email1 = mail.outbox[1]
        self.assertEqual(email0.to[0], signup_default_namespace.recipient)
        self.assertEqual(email1.to[0], signup_new_namespace.recipient)

        # test that emails have correct unsubscribe links
        with override(signup_default_namespace.default_language):
            unsubscribe_link_default_namespace = reverse(
                '{0}:unsubscribe_from_newsletter'.format(
                    signup_default_namespace.app_config.namespace),
                kwargs={'key': signup_default_namespace.confirmation_key}
            )
            opening_link_default_namespace = opening_default.get_absolute_url()

        with override(signup_new_namespace.default_language):
            unsubscribe_link_new_namespace = reverse(
                '{0}:unsubscribe_from_newsletter'.format(
                    signup_new_namespace.app_config.namespace),
                kwargs={'key': signup_new_namespace.confirmation_key}
            )
            opening_link_new_namespace = opening_new_config.get_absolute_url()

        # test unsubscribe links are present in the email
        self.assertNotEqual(
            email0.body.find(unsubscribe_link_default_namespace), -1)
        self.assertNotEqual(
            email1.body.find(unsubscribe_link_new_namespace), -1)

        # test job opening links are present in the emails
        self.assertNotEqual(
            email0.body.find(opening_link_default_namespace), -1)
        self.assertNotEqual(
            email1.body.find(opening_link_new_namespace), -1)
        # test that job links from different namespace are absent
        self.assertEqual(
            email0.body.find(opening_link_new_namespace), -1)
        self.assertEqual(
            email1.body.find(opening_link_default_namespace), -1)

    def test_disabled_users_do_not_get_newsletter(self):
        # setup another apphooked page, since reload takes some time
        # we will setup apphook on the beginning of a test case
        new_config = JobsConfig.objects.create(namespace='new_appconfig')
        self.create_page(
            title='Another apphooked jobs',
            slug='another-apphooked-jobs',
            namespace=new_config.namespace)

        # prepare signups
        # signup_default_namespace
        NewsletterSignup.objects.create(
            recipient='initial@reicipent.com',
            is_verified=True,
            is_disabled=True,
            default_language='en',
            app_config=self.app_config,
            confirmation_key=NewsletterSignup.objects.generate_random_key())
        # signup_new_namespace
        NewsletterSignup.objects.create(
            recipient='new@reicipent.com',
            is_verified=True,
            is_disabled=True,
            default_language='en',
            app_config=new_config,
            confirmation_key=NewsletterSignup.objects.generate_random_key())

        # prepare job opening
        opening_default = self.create_default_job_opening(translated=True)
        with override('en'):
            category_new_config = JobCategory.objects.create(
                app_config=new_config,
                **self.make_new_values(self.category_values_raw['en'], 1)
            )
            opening_new_config = JobOpening.objects.create(
                category=category_new_config,
                **self.make_new_values(self.opening_values_raw['en'], 1)
            )

        # send newsletter
        NewsletterSignup.objects.send_job_notifiation(
            job_list=[job.pk for job in (opening_default, opening_new_config)])

        self.assertEqual(len(mail.outbox), 0)
