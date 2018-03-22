# -*- coding: utf-8 -*-

from .base import JobsBaseTestCase


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
            'job_opening_content': '<p>Needs skills in Python/Django.</p>',
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
