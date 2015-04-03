# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import aldryn_categories.fields


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_jobs', '0009_auto_20150403_0611'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobcategory',
            name='app_config',
        ),
        migrations.RemoveField(
            model_name='jobcategory',
            name='supervisors',
        ),
        migrations.AlterUniqueTogether(
            name='jobcategorytranslation',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='jobcategorytranslation',
            name='master',
        ),
        migrations.DeleteModel(
            name='JobCategoryTranslation',
        ),
        migrations.AlterModelOptions(
            name='joboffer',
            options={'ordering': ['category', '-created'], 'verbose_name': 'Job offer', 'verbose_name_plural': 'Job offers'},
        ),
        migrations.RemoveField(
            model_name='joboffer',
            name='category',
        ),
        migrations.RenameField(
            model_name='joboffer',
            old_name='category_new',
            new_name='category'
        ),

        migrations.DeleteModel(
            name='JobCategory',
        ),
    ]
