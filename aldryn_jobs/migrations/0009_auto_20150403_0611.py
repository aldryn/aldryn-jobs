# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from aldryn_categories.models import Category as NoFrozenCategory


def forwards(apps, schema_editor):
    "Write your forwards methods here."
    # Note: Don't use "from appname.models import ModelName".
    # Use orm.ModelName to refer to models in this application,
    # and orm['appname.ModelName'] for models in other applications.
    Category = apps.get_model('aldryn_categories.Category')
    JobCategory = apps.get_model('aldryn_jobs.JobCategory')
    JobCategoryOpts = apps.get_model('aldryn_jobs.JobCategoryOpts')
    for old_category in JobCategory.objects.all():
        # This is maybe wrong but using the model out of 'orm' (not frozen)
        # we can access add_root. Copy all the treebeard category creation
        # into migration is a big overhead, but would be the perfect thing
        # to do.
        en_tr = old_category.translations.get(language_code='en')
        new_category = NoFrozenCategory.add_root(
            name=en_tr.name,
            slug=en_tr.slug,
        )
        new_category = Category.objects.get(pk=new_category.pk)

        # When creating default translation parler use as default 'en-us',
        # so we fix it here because we use only 'en'.
        en_tr = new_category.translations.get()
        en_tr.language_code = 'en'
        en_tr.save()

        # add other translations, we can't use create_translations
        # in migrations.
        for tr in old_category.translations.exclude(language_code='en'):
            new_category.translations.create(
                language_code=tr.language_code,
                name=tr.name,
                slug=tr.slug,
            )

        for job in old_category.jobs.all():
            job.category_new = new_category
            job.category = None
            job.save()

        job_opts = JobCategoryOpts.objects.create(
            category_id=new_category.pk,
            app_config=old_category.app_config,
            # ordering isn't migrated since aldryn-categories provide a way
            # to order categories already
        )
        job_opts.supervisors = old_category.supervisors.all()
        job_opts.save()

        old_category.delete()


def backwards(apps, schema_editor):
    "Write your backwards methods here."
    Category = apps.get_model('aldryn_categories.Category')
    JobCategory = apps.get_model('aldryn_jobs.JobCategory')
    JobCategoryOpts = apps.get_model('aldryn_jobs.JobCategoryOpts')

    for new_category in Category.objects.all():
        job_opt = JobCategoryOpts.objects.get(category=new_category)
        # create the old category
        old_category = JobCategory.objects.create(
            app_config=job_opt.app_config
        )
        old_category.supervisors = job_opt.supervisors.all()

        # create default translation
        en_tr = new_category.translations.get(language_code='en')
        old_category.translations.create(
            language_code='en',
            name=en_tr.name,
            slug=en_tr.slug
        )
        for tr in new_category.translations.exclude(language_code='en'):
            # create another translations
            old_category.translations.create(
                language_code=tr.language_code,
                name=tr.name,
                slug=tr.slug,
            )

        for job in new_category.job_offers.all():
            job.category = old_category
            job.category_new = None
            job.save()

        old_category.save()
        new_category.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_jobs', '0008_auto_20150403_0611'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards)
    ]
