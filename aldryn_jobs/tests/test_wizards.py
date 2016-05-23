# -*- coding: utf-8 -*-
import sys

from distutils.version import LooseVersion

import cms

from .base import JobsBaseTestCase

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

# The CMS wizard system was introduced in 3.2.0
CMS_3_2 = LooseVersion(cms.__version__) >= LooseVersion('3.2.0')


@unittest.skipUnless(CMS_3_2, "No wizard support in CMS < 3.2")
class TestJobsWizard(JobsBaseTestCase):

    def setUp(self):
        super(TestJobsWizard, self).setUp()
        self.client.login(
            username=self.super_user.username,
            password=self.super_user_password,
        )

    def test_job_opening_wizard(self):
        # Import here to avoid logic wizard machinery
        from aldryn_jobs.cms_wizards import CreateJobOpeningForm

        data = {
            'title': 'Ninja coder',
            'lead_in': 'Ninja coder wanted',
            'content': '<p>Needs skills in Python/Django.</p>',
            'is_active': True,
            'category': self.default_category.pk,
        }
        form = CreateJobOpeningForm(
            data=data,
            wizard_language='en',
            wizard_user=self.super_user,
        )
        self.assertTrue(form.is_valid())
        question = form.save()

        url = question.get_absolute_url('en')
        response = self.client.get(url)
        self.assertContains(response, 'Ninja coder', status_code=200)
        self.assertContains(
            response,
            '<p>Needs skills in Python/Django.</p>',
            status_code=200,
        )
