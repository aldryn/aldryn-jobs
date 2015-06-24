# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_categories', '0003_auto_20150128_1359'),
        ('aldryn_jobs', '0008_jobcategorynew'),
    ]

    operations = [
        # FIXME: Decide if we should delete those tables/fields
        migrations.RemoveField(
            model_name='jobcategorynew',
            name='app_config',
        ),
        # FIXME: Decide if we should delete those tables/fields
        migrations.RemoveField(
            model_name='jobcategorynew',
            name='category_ptr',
        ),
        # FIXME: Decide if we should delete those tables/fields
        migrations.RemoveField(
            model_name='jobcategorynew',
            name='supervisors',
        ),
        # FIXME: Decide if we should delete those tables/fields
        migrations.DeleteModel(
            name='JobCategoryNew',
        ),
        # FIXME: most likely we need to delete this
        # this most likely is related to different version of parler
        # different from setup in which previous migration were created
        migrations.AlterModelOptions(
            name='jobcategorytranslation',
            options={'default_permissions': (), 'verbose_name': 'Job category Translation', 'managed': True},
        ),
        # FIXME: most likely we need to delete this
        # this most likely is related to different version of parler
        # different from setup in which previous migration were created
        migrations.AlterModelOptions(
            name='joboffertranslation',
            options={'default_permissions': (), 'verbose_name': 'Job offer Translation', 'managed': True},
        ),
        migrations.AddField(
            model_name='jobnewsletterregistrationplugin',
            name='app_config',
            field=models.ForeignKey(verbose_name='app_config', to='aldryn_jobs.JobsConfig', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='newslettersignup',
            name='app_config',
            field=models.ForeignKey(verbose_name='app_config', to='aldryn_jobs.JobsConfig', null=True),
            preserve_default=True,
        ),
        # FIXME: most likely we need to delete this
        # this most likely is related to different version of parler
        # different from setup in which previous migration were created
        migrations.AlterField(
            model_name='jobcategorytranslation',
            name='language_code',
            field=models.CharField(max_length=15, verbose_name='Language', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jobnewsletterregistrationplugin',
            name='mail_to_group',
            field=models.ManyToManyField(help_text='If user successfuly completed registration.<br/>Notification would be sent to users from selected groups<br/>Leave blank to disable notifications.<br/>', to='auth.Group', verbose_name='Notification to', blank=True),
            preserve_default=True,
        ),
        # FIXME: most likely we need to delete this
        # this most likely is related to different version of parler
        # different from setup in which previous migration were created
        migrations.AlterField(
            model_name='joboffertranslation',
            name='language_code',
            field=models.CharField(max_length=15, verbose_name='Language', db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jobsconfig',
            name='namespace',
            field=models.CharField(default=None, unique=True, max_length=100, verbose_name='instance namespace'),
            preserve_default=True,
        ),
    ]
