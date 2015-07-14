# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import reversion
import six

from django.db import transaction
from parler.utils.context import switch_language

from aldryn_reversion.core import create_revision_with_placeholders

from ..models import JobCategory, JobOpening, JobApplication
from .base import JobsBaseTestCase


class ReversionTestCase(JobsBaseTestCase):
    """
    Cover reversion support, test cases:
     * revisions are created (reversions and self test)
     * revisions are reverted (reversions and self test)
     * not translated fields are changed when new revision is created
     * not translated fields are being reverted correctly
     * translated fields are changed on save with revision (latest change
       should be shown)
     * translated fields are reverted correctly
     * placeholder fields are reverted with correct plugins (according
       to revision)
     * [TBD] placeholder fields for translated objects should serve correct
       plugins for translation
     * [TBD] placeholder fields for translated objects should server correct
       plugins for translation after revision revert.
    """

    def create_revision(self, obj, content=None, **kwargs):
        with transaction.atomic():
            with reversion.create_revision():
                # populate event with new values
                for property, value in six.iteritems(kwargs):
                    setattr(obj, property, value)
                if content:
                    # get correct plugin for language. do not update the same
                    # one.
                    language = obj.get_current_language()
                    plugins = obj.content.get_plugins().filter(
                        language=language)
                    plugin = plugins[0].get_plugin_instance()[0]
                    plugin.body = content
                    plugin.save()
                obj.save()

    def revert_to(self, object_with_revision, revision_number):
        """
        Revert <object with revision> to revision number.
        """
        # get by position, since reversion_id is not reliable,
        version = list(reversed(
            reversion.get_for_object(
                object_with_revision)))[revision_number - 1]
        version.revision.revert()

    # Following tests does not covers translations!
    def test_revision_is_created_on_job_category_object_create(self):
        with transaction.atomic():
            with reversion.create_revision():
                job_category = JobCategory.objects.create(
                    app_config=self.app_config,
                    **self.category_values_raw['en'])
        self.assertEqual(len(reversion.get_for_object(job_category)), 1)

    def test_revision_is_created_on_job_opening_object_created(self):
        with transaction.atomic():
            with reversion.create_revision():
                job_opening = JobOpening.objects.create(
                    category=self.default_category,
                    **self.opening_values_raw['en'])
        self.assertEqual(len(reversion.get_for_object(job_opening)), 1)

    def test_category_revision_is_created(self):
        category = JobCategory.objects.create(
            app_config=self.app_config,
            **self.category_values_raw['en'])
        self.assertEqual(len(reversion.get_for_object(category)), 0)
        new_values_en_1 = self.make_new_values(
            self.category_values_raw['en'], 1)
        self.create_revision(category, **new_values_en_1)
        self.assertEqual(len(reversion.get_for_object(category)), 1)

    def test_job_opening_revision_is_created(self):
        job_opening = self.create_default_job_opening()
        self.assertEqual(len(reversion.get_for_object(job_opening)), 0)

        new_values_en_1 = self.make_new_values(
            self.default_job_values['en'], 1)
        self.create_revision(job_opening, **new_values_en_1)
        self.assertEqual(len(reversion.get_for_object(job_opening)), 1)

    def test_category_with_one_revision_contains_latest_values(self):
        category = JobCategory.objects.create(
            app_config=self.app_config,
            **self.category_values_raw['en'])
        new_values_en_1 = self.make_new_values(
            self.category_values_raw['en'], 1)
        # revision 1
        self.create_revision(category, **new_values_en_1)
        for prop in new_values_en_1.keys():
            self.assertEqual(getattr(category, prop), new_values_en_1[prop])

        # the same but with re-getting category object
        category = JobCategory.objects.get(pk=category.pk)
        for prop in new_values_en_1.keys():
            self.assertEqual(getattr(category, prop), new_values_en_1[prop])

    def test_opening_with_one_revision_contains_latest_values(self):
        job_opening = self.create_default_job_opening()
        # revision 1
        new_values_en_1 = self.make_new_values(self.opening_values_raw['en'], 1)
        content_en_1 = self.plugin_values_raw['en'].format(1)
        self.create_revision(
            job_opening, content=content_en_1, **new_values_en_1)

        job_opening = JobOpening.objects.get(pk=job_opening.pk)
        for prop in new_values_en_1.keys():
            self.assertEqual(getattr(job_opening, prop), new_values_en_1[prop])

    def test_opening_with_one_revision_serves_latest_content(self):
        job_opening = self.create_default_job_opening()
        # revision 1
        new_values_en_1 = self.make_new_values(self.opening_values_raw['en'], 1)
        content_en_1 = self.plugin_values_raw['en'].format(1)
        self.create_revision(
            job_opening, content=content_en_1, **new_values_en_1)

        # test url and served content
        with switch_language(job_opening, 'en'):
            url_1 = job_opening.get_absolute_url()
        response = self.client.get(url_1)
        self.assertContains(response, new_values_en_1['title'])
        self.assertContains(response, content_en_1)

    def test_category_with_two_revision_contains_latest_values(self):
        category = JobCategory.objects.create(
            app_config=self.app_config,
            **self.category_values_raw['en'])
        # revision 1
        new_values_en_1 = self.make_new_values(
            self.category_values_raw['en'], 1)
        self.create_revision(category, **new_values_en_1)

        # revision 2
        new_values_en_2 = self.make_new_values(
            self.category_values_raw['en'], 2)
        self.create_revision(category, **new_values_en_2)

        for prop in new_values_en_2.keys():
            self.assertEqual(getattr(category, prop), new_values_en_2[prop])

        # the same but with re-getting category object
        category = JobCategory.objects.get(pk=category.pk)
        for prop in new_values_en_2.keys():
            self.assertEqual(getattr(category, prop), new_values_en_2[prop])

    def test_opening_with_two_revision_contains_latest_values(self):
        job_opening = self.create_default_job_opening()

        # revision 1
        new_values_en_1 = self.make_new_values(self.opening_values_raw['en'], 1)
        content_en_1 = self.plugin_values_raw['en'].format(1)
        self.create_revision(
            job_opening, content=content_en_1, **new_values_en_1)

        # revision 2
        new_values_en_2 = self.make_new_values(self.opening_values_raw['en'], 2)
        content_en_2 = self.plugin_values_raw['en'].format(2)
        self.create_revision(
            job_opening, content=content_en_2, **new_values_en_2)

        job_opening = JobOpening.objects.get(pk=job_opening.pk)
        for prop in new_values_en_2.keys():
            self.assertEqual(getattr(job_opening, prop), new_values_en_2[prop])

    def test_opening_with_two_revision_serves_latest_content(self):
        job_opening = self.create_default_job_opening()

        # revision 1
        new_values_en_1 = self.make_new_values(self.opening_values_raw['en'], 1)
        content_en_1 = self.plugin_values_raw['en'].format(1)
        self.create_revision(
            job_opening, content=content_en_1, **new_values_en_1)

        # revision 2
        new_values_en_2 = self.make_new_values(self.opening_values_raw['en'], 2)
        content_en_2 = self.plugin_values_raw['en'].format(2)
        self.create_revision(
            job_opening, content=content_en_2, **new_values_en_2)

        # test served title
        job_opening = JobOpening.objects.get(pk=job_opening.pk)
        with switch_language(job_opening, 'en'):
            url = job_opening.get_absolute_url()
        response = self.client.get(url)
        self.assertContains(response, new_values_en_2['title'])
        self.assertContains(response, content_en_2)
        # legacy values/content
        self.assertNotContains(response, new_values_en_1['title'])
        self.assertNotContains(response, content_en_1)

    def test_category_revisions_are_reverted(self):
        # no revisions at this point
        category = JobCategory.objects.create(
            app_config=self.app_config,
            **self.category_values_raw['en'])

        # revision 1
        new_values_en_1 = self.make_new_values(
            self.category_values_raw['en'], 1)
        self.create_revision(category, **new_values_en_1)

        # revision 2
        new_values_en_2 = self.make_new_values(
            self.category_values_raw['en'], 2)
        self.create_revision(category, **new_values_en_2)

        # revert to 1
        self.revert_to(category, 1)

        category = JobCategory.objects.get(pk=category.pk)
        for prop in new_values_en_1.keys():
            self.assertEqual(getattr(category, prop), new_values_en_1[prop])

    def test_opening_revisions_are_reverted(self):
        job_opening = self.create_default_job_opening()

        # revision 1
        new_values_en_1 = self.make_new_values(self.opening_values_raw['en'], 1)
        content_en_1 = self.plugin_values_raw['en'].format(1)
        self.create_revision(
            job_opening, content=content_en_1, **new_values_en_1)

        # revision 2
        new_values_en_2 = self.make_new_values(self.opening_values_raw['en'], 2)
        content_en_2 = self.plugin_values_raw['en'].format(2)
        new_category = JobCategory.objects.create(
            app_config=self.app_config,
            **self.make_new_values(self.category_values_raw['en'], 2))
        new_values_en_2['category'] = new_category
        self.create_revision(
            job_opening, content=content_en_2, **new_values_en_2)

        # revert to 1
        self.revert_to(job_opening, 1)
        job_opening = JobOpening.objects.get(pk=job_opening.pk)
        new_values_en_1['category'] = self.default_category
        for prop in new_values_en_1.keys():
            self.assertEqual(getattr(job_opening, prop), new_values_en_1[prop])
        self.assertNotEqual(job_opening.category, new_category)

    def test_opening_reverted_revision_serves_appropriate_content(self):
        job_opening = self.create_default_job_opening()

        # revision 1
        new_values_en_1 = self.make_new_values(self.opening_values_raw['en'], 1)
        content_en_1 = self.plugin_values_raw['en'].format(1)
        self.create_revision(
            job_opening, content=content_en_1, **new_values_en_1)

        # revision 2
        new_values_en_2 = self.make_new_values(self.opening_values_raw['en'], 2)
        content_en_2 = self.plugin_values_raw['en'].format(2)
        self.create_revision(
            job_opening, content=content_en_2, **new_values_en_2)

        # revert to 1
        job_opening = JobOpening.objects.get(pk=job_opening.pk)
        self.revert_to(job_opening, 1)
        job_opening = JobOpening.objects.get(pk=job_opening.pk)
        with switch_language(job_opening, 'en'):
            url = job_opening.get_absolute_url()
        response = self.client.get(url)
        self.assertContains(response, new_values_en_1['title'])
        self.assertContains(response, content_en_1)
        self.assertNotContains(response, new_values_en_2['title'])
        self.assertNotContains(response, content_en_2)

    def test_edit_plugin_directly(self):
        job_opening = self.create_default_job_opening()

        # revision 1
        content_en_1 = self.plugin_values_raw['en'].format(1)
        self.create_revision(job_opening, content=content_en_1)

        self.assertEqual(len(reversion.get_for_object(job_opening)), 1)

        # revision 2
        content_en_2 = self.plugin_values_raw['en'].format(2)
        with transaction.atomic():
            with reversion.create_revision():
                language = job_opening.get_current_language()
                plugins = job_opening.content.get_plugins().filter(
                    language=language)
                plugin = plugins[0].get_plugin_instance()[0]
                plugin.body = content_en_2
                plugin.save()
                create_revision_with_placeholders(job_opening)
        self.assertEqual(len(reversion.get_for_object(job_opening)), 2)

        with switch_language(job_opening, 'en'):
            url = job_opening.get_absolute_url()
        response = self.client.get(url)

        self.assertContains(response, content_en_2)
        self.assertNotContains(response, content_en_1)

        self.revert_to(job_opening, 1)
        job_opening = JobOpening.objects.get(pk=job_opening.pk)
        response = self.client.get(job_opening.get_absolute_url())
        self.assertContains(response, content_en_1)
        self.assertNotContains(response, content_en_2)

    def test_category_revert_revision_correct_for_diverged_translations(self):
        category = self.default_category
        self.assertEqual(len(reversion.get_for_object(category)), 0)
        # revision 1: en 1, de 0
        new_values = self.make_new_values(self.category_values_raw['en'], 1)
        with switch_language(category, 'en'):
            self.create_revision(category, **new_values)

        # revision 2: en 1, de 1
        new_values_2 = self.make_new_values(self.category_values_raw['de'], 1)
        with switch_language(category, 'de'):
            self.create_revision(category, **new_values_2)

        # revision 3: en 1, de 2
        new_values_3 = self.make_new_values(self.category_values_raw['de'], 2)
        with switch_language(category, 'de'):
            self.create_revision(category, **new_values_3)

        # revision 4: en 2, de 2
        with switch_language(category, 'en'):
            new_values_4 = self.make_new_values(
                self.category_values_raw['en'], 2)
            self.create_revision(category, **new_values_4)

        # revert to 3: en 1, de 2
        self.revert_to(category, 3)
        category = JobCategory.objects.get(pk=category.pk)
        # test en values
        # switch_language(category,
        with switch_language(category, 'en'):
            for prop in new_values.keys():
                self.assertEqual(getattr(category, prop), new_values[prop])
        # test de values
        with switch_language(category, 'de'):
            for prop in new_values_3.keys():
                self.assertEqual(getattr(category, prop), new_values_3[prop])

    def test_opening_revert_revision_correct_for_diverged_translations(self):
        opening = self.create_default_job_opening(translated=True)
        self.assertEqual(len(reversion.get_for_object(opening)), 0)
        initial_values = {
            'category': self.default_category,
            'is_active': True,
            'can_apply': True,
        }
        # revision 1: en 1, de 0
        new_values_en_1 = self.make_new_values(self.opening_values_raw['en'], 1)
        with switch_language(opening, 'en'):
            self.create_revision(opening, **new_values_en_1)

        # revision 2: en 1, de 1
        new_values_de_1 = self.make_new_values(self.opening_values_raw['de'], 1)
        with switch_language(opening, 'de'):
            self.create_revision(opening, **new_values_de_1)

        # revision 3: en 1, de 2
        new_values_de_2 = self.make_new_values(self.opening_values_raw['de'], 2)
        with switch_language(opening, 'de'):
            self.create_revision(opening, **new_values_de_2)

        # revision 4: en 2, de 2, also contains updated category and bool fields
        new_values_en_2 = self.make_new_values(self.opening_values_raw['en'], 2)
        new_category = JobCategory.objects.create(
            app_config=self.app_config,
            **self.make_new_values(self.category_values_raw['en'], 2))
        new_values_en_2['category'] = new_category
        new_values_en_2['is_active'] = False
        new_values_en_2['can_apply'] = False
        with switch_language(opening, 'en'):
            self.create_revision(opening, **new_values_en_2)

        # revert to 3: en 1, de 2
        self.revert_to(opening, 3)
        opening = JobOpening.objects.get(pk=opening.pk)
        # test en values
        with switch_language(opening, 'en'):
            for prop in new_values_en_1.keys():
                self.assertEqual(getattr(opening, prop), new_values_en_1[prop])
            # test untranslated fields, should be the same as atm of reverted
            # revision
            for prop in initial_values.keys():
                self.assertEqual(getattr(opening, prop), initial_values[prop])

        # test de values
        with switch_language(opening, 'de'):
            for prop in new_values_de_2.keys():
                self.assertEqual(getattr(opening, prop), new_values_de_2[prop])
            # test untranslated fields shouldn't be changed regardless of
            # language
            for prop in initial_values.keys():
                self.assertEqual(getattr(opening, prop), initial_values[prop])

    def test_opening_revert_revision_serves_for_diverged_translations(self):
        opening = self.create_default_job_opening(translated=True)
        self.assertEqual(len(reversion.get_for_object(opening)), 0)

        # revision 1: en 1, de 0
        new_values_en_1 = self.make_new_values(self.opening_values_raw['en'], 1)
        content_en_1 = self.plugin_values_raw['en'].format(1)
        with switch_language(opening, 'en'):
            self.create_revision(
                opening, content=content_en_1, **new_values_en_1)

        # revision 2: en 1, de 1
        new_values_de_1 = self.make_new_values(self.opening_values_raw['de'], 1)
        content_de_1 = self.plugin_values_raw['de'].format(1)
        with switch_language(opening, 'de'):
            self.create_revision(
                opening, content=content_de_1, **new_values_de_1)

        # revision 3: en 1, de 2
        new_values_de_2 = self.make_new_values(self.opening_values_raw['de'], 2)
        content_de_2 = self.plugin_values_raw['de'].format(2)
        with switch_language(opening, 'de'):
            self.create_revision(
                opening, content=content_de_2, **new_values_de_2)

        # revision 4: en 2, de 2
        content_en_2 = self.plugin_values_raw['en'].format(2)
        new_values_en_2 = self.make_new_values(self.opening_values_raw['en'], 2)
        with switch_language(opening, 'en'):
            self.create_revision(
                opening, content=content_en_2, **new_values_en_2)

        # revert to 3: en 1, de 2
        self.revert_to(opening, 3)
        opening = JobOpening.objects.get(pk=opening.pk)
        # test en values
        with switch_language(opening, 'en'):
            url_reverted_en = opening.get_absolute_url()
        response = self.client.get(url_reverted_en)
        self.assertContains(response, new_values_en_1['title'])
        self.assertContains(response, content_en_1)
        # ensure that there is no latest values (rev 4)
        self.assertNotContains(response, new_values_en_2['title'])
        self.assertNotContains(response, content_en_2)
        # test de values
        with switch_language(opening, 'de'):
            url_reverted_de = opening.get_absolute_url()
        response = self.client.get(url_reverted_de)
        self.assertContains(response, new_values_de_2['title'])
        self.assertContains(response, content_de_2)
        # ensure that there is no previous values (rev 2)
        self.assertNotContains(response, new_values_de_1['title'])
        self.assertNotContains(response, content_de_1)

    def test_opening_is_reverted_if_fk_object_was_deleted(self):
        opening = self.create_default_job_opening(translated=True)
        self.assertEqual(len(reversion.get_for_object(opening)), 0)

        # revision 1: en 1, de 0
        category_1 = self.default_category
        new_values_en_1 = self.make_new_values(self.opening_values_raw['en'], 1)
        with switch_language(opening, 'en'):
            self.create_revision(opening, **new_values_en_1)

        # revision 2: en 1, de 1
        new_values_de_1 = self.make_new_values(self.opening_values_raw['de'], 1)
        # update category
        category_2 = JobCategory.objects.create(
            app_config=self.app_config,
            **self.make_new_values(self.category_values_raw['en'], 2))
        new_values_de_1['category'] = category_2
        with switch_language(opening, 'de'):
            self.create_revision(opening, **new_values_de_1)

        # delete category_1
        with transaction.atomic():
            category_1.delete()
        self.assertEqual(JobCategory.objects.all().count(), 1)

        # revert to 1
        self.revert_to(opening, 1)
        opening = JobOpening.objects.get(pk=opening.pk)
        self.assertNotEqual(opening.category, category_2)
        self.assertEqual(JobCategory.objects.all().count(), 2)

    # JobApplication
    def test_job_application_revision_is_created(self):
        job_opening = self.create_default_job_opening()
        application = JobApplication.objects.create(
            job_opening=job_opening,
            **self.application_default_values)
        self.assertEqual(len(reversion.get_for_object(application)), 0)

        # revision 1
        new_values_1 = self.make_new_values(self.application_values_raw, 1)
        self.create_revision(application, **new_values_1)
        self.assertEqual(len(reversion.get_for_object(application)), 1)

    def test_job_application_contains_latest_values(self):
        job_opening = self.create_default_job_opening()
        application = JobApplication.objects.create(
            job_opening=job_opening,
            **self.application_default_values)

        # revision 1
        new_values_1 = self.make_new_values(self.application_values_raw, 1)
        self.create_revision(application, **new_values_1)
        self.assertEqual(len(reversion.get_for_object(application)), 1)

        application = JobApplication.objects.get(pk=application.pk)
        for prop in new_values_1.keys():
            self.assertEqual(getattr(application, prop), new_values_1[prop])

        # revision 2
        new_values_2 = self.make_new_values(self.application_values_raw, 2)
        new_opening = JobOpening.objects.create(
            category=self.default_category,
            **self.make_new_values(self.opening_values_raw['en'], 2))
        new_values_2['job_opening'] = new_opening
        self.create_revision(application, **new_values_2)
        self.assertEqual(len(reversion.get_for_object(application)), 2)

        application = JobApplication.objects.get(pk=application.pk)
        for prop in new_values_2.keys():
            self.assertEqual(getattr(application, prop), new_values_2[prop])

    def test_job_application_revision_is_reverted(self):
        job_opening = self.create_default_job_opening()
        application = JobApplication.objects.create(
            job_opening=job_opening, **self.application_default_values)

        # revision 1
        new_values_1 = self.make_new_values(self.application_values_raw, 1)
        self.create_revision(application, **new_values_1)
        self.assertEqual(len(reversion.get_for_object(application)), 1)

        # revision 2
        new_values_2 = self.make_new_values(self.application_values_raw, 2)
        new_opening = JobOpening.objects.create(
            category=self.default_category,
            **self.make_new_values(self.opening_values_raw['en'], 2))
        new_values_2['job_opening'] = new_opening
        self.create_revision(application, **new_values_2)
        self.assertEqual(len(reversion.get_for_object(application)), 2)

        # revert to 1
        self.revert_to(application, 1)
        application = JobApplication.objects.get(pk=application.pk)
        # add initial job_opening to values list to be checked
        new_values_1['job_opening'] = job_opening
        for prop in new_values_1.keys():
            self.assertEqual(getattr(application, prop), new_values_1[prop])

    def test_job_application_revision_is_reverted_if_fk_obj_was_deleted(self):
        job_opening = self.create_default_job_opening()
        application = JobApplication.objects.create(
            job_opening=job_opening, **self.application_default_values)

        # revision 1
        new_values_1 = self.make_new_values(self.application_values_raw, 1)
        self.create_revision(application, **new_values_1)
        self.assertEqual(len(reversion.get_for_object(application)), 1)

        # revision 2
        new_values_2 = self.make_new_values(self.application_values_raw, 2)
        new_opening = JobOpening.objects.create(
            category=self.default_category,
            **self.make_new_values(self.opening_values_raw['en'], 2))
        new_values_2['job_opening'] = new_opening
        self.create_revision(application, **new_values_2)
        self.assertEqual(len(reversion.get_for_object(application)), 2)

        # delete initial opening
        with transaction.atomic():
            job_opening.delete()

        # revert to 1
        self.revert_to(application, 1)
        application = JobApplication.objects.get(pk=application.pk)
        self.assertEqual(JobOpening.objects.all().count(), 2)
        # get restored job opening
        job_opening = JobOpening.objects.all().exclude(pk=new_opening.pk).get()
        # add initial job_opening to values list to be checked
        new_values_1['job_opening'] = job_opening
        for prop in new_values_1.keys():
            self.assertEqual(getattr(application, prop), new_values_1[prop])
