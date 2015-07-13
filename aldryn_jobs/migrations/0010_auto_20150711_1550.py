# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app_data.fields


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_categories', '0004_auto_20150623_0859'),
        ('aldryn_jobs', '0009_auto_20150624_1649'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobcategorynew',
            name='app_config',
        ),
        migrations.RemoveField(
            model_name='jobcategorynew',
            name='category_ptr',
        ),
        migrations.RemoveField(
            model_name='jobcategorynew',
            name='supervisors',
        ),
        migrations.DeleteModel(
            name='JobCategoryNew',
        ),
        migrations.AlterModelOptions(
            name='jobcategorytranslation',
            options={'default_permissions': (), 'managed': True, 'verbose_name': 'Job category Translation'},
        ),
        migrations.AlterModelOptions(
            name='joboffertranslation',
            options={'default_permissions': (), 'managed': True, 'verbose_name': 'Job offer Translation'},
        ),
        migrations.RemoveField(
            model_name='jobapplication',
            name='app_config',
        ),
        migrations.AlterField(
            model_name='jobapplication',
            name='created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jobapplication',
            name='is_rejected',
            field=models.BooleanField(default=False, verbose_name='rejected?'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jobapplication',
            name='rejection_date',
            field=models.DateTimeField(null=True, blank=True, verbose_name='rejection date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jobapplication',
            name='salutation',
            field=models.CharField(blank=True, default='male', max_length=20, verbose_name='Salutation', choices=[('male', 'Mr.'), ('female', 'Mrs.')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jobcategorytranslation',
            name='language_code',
            field=models.CharField(max_length=15, verbose_name='Language', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='joboffertranslation',
            name='language_code',
            field=models.CharField(max_length=15, verbose_name='Language', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jobsconfig',
            name='app_data',
            field=app_data.fields.AppDataField(default='{}', editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='newslettersignup',
            name='default_language',
            field=models.CharField(blank=True, default='', max_length=32, verbose_name='language', choices=[('en', 'English'), ('de', 'German')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='newslettersignup',
            name='recipient',
            field=models.EmailField(unique=True, max_length=75, verbose_name='recipient'),
            preserve_default=True,
        ),
    ]
