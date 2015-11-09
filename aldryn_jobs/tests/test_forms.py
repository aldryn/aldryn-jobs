from ..cms_appconfig import JobsConfig
from ..models import JobCategory
from ..forms import JobCategoryAdminForm, JobOpeningAdminForm

from .base import JobsBaseTestCase


class JobCategoryAdminFormTestCase(JobsBaseTestCase):

    def test_form_not_valid_if_app_config_not_selected(self):
        # and it produces validation error instead of 500
        data = {
            'name': self.default_category_values['en']['name'],
            'slug': 'default-category-different-slug',
        }
        form = JobCategoryAdminForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('app_config', form.errors.keys())

    def test_form_not_valid_no_data_provided_at_all(self):
        # and it produces validation error instead of 500
        data = {}
        form = JobCategoryAdminForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('app_config', form.errors.keys())
        self.assertIn('name', form.errors.keys())

    def test_form_not_valid_if_only_app_config_was_selected(self):
        # and it produces validation error instead of 500
        data = {'app_config': self.app_config.pk}
        form = JobCategoryAdminForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors.keys())

    def test_form_not_valid_if_only_name_was_provided(self):
        # and it produces validation error instead of 500
        data = {'name': self.default_category_values['en']['name']}
        form = JobCategoryAdminForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('app_config', form.errors.keys())

    def test_form_not_valid_if_only_slug_was_provided(self):
        # and it produces validation error instead of 500
        data = {
            'slug': 'default-category-different-slug',
        }
        form = JobCategoryAdminForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors.keys())
        self.assertIn('app_config', form.errors.keys())

    def test_form_valid_for_same_name_in_different_app_config(self):
        other_config = JobsConfig.objects.create(namespace='other_config')
        data = {
            'app_config': other_config.pk,
            'name': self.default_category_values['en']['name'],
            'slug': 'default-category-different-slug',
        }
        form = JobCategoryAdminForm(data)
        self.assertTrue(form.is_valid())
        new_category = form.save()
        self.assertEqual(new_category.name,
                         data['name'])
        self.assertEqual(new_category.slug,
                         data['slug'])
        self.assertEqual(new_category.app_config, other_config)

    def test_form_valid_for_same_slug_in_different_app_config(self):
        # depends on decision if we will remove uniqueness of slug per language
        other_config = JobsConfig.objects.create(namespace='other_config')
        data = {
            'name': 'different name',
            'slug': self.default_category_values['en']['slug'],
            'app_config': other_config.pk,
        }
        data.update(self.default_category_values['en'])
        form = JobCategoryAdminForm(data)
        self.assertTrue(form.is_valid())
        # test new category values
        new_category = form.save()
        self.assertEqual(new_category.name,
                         data['name'])
        self.assertEqual(new_category.slug,
                         data['slug'])
        self.assertEqual(new_category.app_config, other_config)

    def test_form_is_valid_for_unique_name(self):
        # form should allow unique names
        data = {
            'name': 'Unique name for category',
            'app_config': self.app_config.pk
        }
        form = JobCategoryAdminForm(data)
        self.assertTrue(form.is_valid())

        # test new category values
        new_category = form.save()
        self.assertEqual(new_category.name,
                         data['name'])
        self.assertGreater(len(new_category.slug), 0)
        self.assertEqual(new_category.app_config, self.app_config)

    def test_form_is_valid_for_unique_slug(self):
        # form should allow unique names
        data = {
            'name': 'Unique name for category with slug',
            'slug': 'unique-name-for-category-with-slug',
            'app_config': self.app_config.pk
        }
        form = JobCategoryAdminForm(data)
        self.assertTrue(form.is_valid())
        # test new category values
        new_category = form.save()
        self.assertEqual(new_category.name,
                         data['name'])
        self.assertGreater(len(new_category.slug), 0)
        self.assertEqual(new_category.app_config, self.app_config)


class JobOpeningAdminFormTestCase(JobsBaseTestCase):

    def test_form_not_valid_if_category_not_selected(self):
        # and it produces validation error instead of 500
        self.create_default_job_opening(translated=True)
        # provide same data as for default opening
        data = {
            'title': self.default_job_values['en']['title'],
            'slug': self.default_job_values['en']['slug'],
        }
        form = JobOpeningAdminForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors.keys())

    def test_form_valid_for_same_name_in_different_category_app_config(self):
        self.create_default_job_opening(translated=True)
        # prepare category with other app config
        other_config = JobsConfig.objects.create(namespace='other_config')
        other_category = JobCategory.objects.create(
            name='Other category', app_config=other_config)

        data = {
            'category': other_category.pk,
            'title': self.default_job_values['en']['title'],
            'slug': 'default-category-different-slug',
        }
        form = JobOpeningAdminForm(data)
        self.assertTrue(form.is_valid())
        new_opening = form.save()
        self.assertEqual(new_opening.title,
                         data['title'])
        self.assertEqual(new_opening.slug,
                         data['slug'])
        self.assertEqual(new_opening.category, other_category)

    def test_form_valid_for_same_slug_in_different_category(self):
        self.create_default_job_opening(translated=True)
        # depends on decision if we will remove uniqueness of slug per language
        other_config = JobsConfig.objects.create(namespace='other_config')
        other_category = JobCategory.objects.create(
            name='Other category', app_config=other_config)

        data = {
            'title': 'different title',
            'slug': self.default_job_values['en']['slug'],
            'category': other_category.pk,
        }
        data.update(self.default_job_values['en'])
        form = JobOpeningAdminForm(data)
        self.assertTrue(form.is_valid())
        # test new category values
        new_opening = form.save()
        self.assertEqual(new_opening.title,
                         data['title'])
        self.assertEqual(new_opening.slug,
                         data['slug'])
        self.assertEqual(new_opening.category, other_category)

    def test_form_is_valid_for_unique_name(self):
        # form should allow unique names
        data = {
            'title': 'Unique title for opening',
            'category': self.default_category.pk
        }
        form = JobOpeningAdminForm(data)
        self.assertTrue(form.is_valid())
        # test new category values
        new_opening = form.save()
        self.assertEqual(new_opening.title,
                         data['title'])
        self.assertGreater(len(new_opening.slug), 0)
        self.assertEqual(new_opening.category, self.default_category)

    def test_form_is_valid_for_unique_slug(self):
        # form should allow unique names
        data = {
            'title': 'Unique title for opening with slug',
            'slug': 'unique-title-for-opening-with-slug',
            'category': self.default_category.pk
        }
        form = JobOpeningAdminForm(data)
        self.assertTrue(form.is_valid())
        # test new category values
        new_opening = form.save()
        self.assertEqual(new_opening.title,
                         data['title'])
        self.assertGreater(len(new_opening.slug), 0)
        self.assertEqual(new_opening.category, self.default_category)
