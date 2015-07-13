# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_jobs', '0013_create_job_config_placeholders'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobcategoriesplugin',
            name='app_config',
            field=models.ForeignKey(null=True, verbose_name='app_config', help_text='Select appropriate add-on configuration for this plugin.', to='aldryn_jobs.JobsConfig'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='joblistplugin',
            name='app_config',
            field=models.ForeignKey(null=True, verbose_name='app_config', help_text='Select appropriate add-on configuration for this plugin.', to='aldryn_jobs.JobsConfig'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='joblistplugin',
            name='joboffers',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text="Select Job Offers to show or don't select any to show last job offers. Note that Job Offers form different app config would be ignored.", to='aldryn_jobs.JobOffer', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jobnewsletterregistrationplugin',
            name='app_config',
            field=models.ForeignKey(null=True, verbose_name='app_config', help_text='Select appropriate add-on configuration for this plugin.', to='aldryn_jobs.JobsConfig'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='newslettersignup',
            name='default_language',
            field=models.CharField(choices=[('en', 'English'), ('de', 'German')], blank=True, verbose_name='language', max_length=32, default=''),
            preserve_default=True,
        ),
    ]
