# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_categories', '0003_auto_20150128_1359'),
        ('aldryn_jobs', '0008_jobcategorynew'),
    ]

    operations = [
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
        migrations.AlterField(
            model_name='jobnewsletterregistrationplugin',
            name='mail_to_group',
            field=models.ManyToManyField(help_text='If user successfuly completed registration.<br/>Notification would be sent to users from selected groups<br/>Leave blank to disable notifications.<br/>', to='auth.Group', verbose_name='Notification to', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jobsconfig',
            name='namespace',
            field=models.CharField(default=None, unique=True, max_length=100, verbose_name='instance namespace'),
            preserve_default=True,
        ),
    ]
