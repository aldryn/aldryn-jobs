# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_jobs', '0002_default_appconfig'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobapplication',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='email'),
        ),
        migrations.AlterField(
            model_name='jobcategoriesplugin',
            name='cmsplugin_ptr',
            field=models.OneToOneField(parent_link=True, related_name='aldryn_jobs_jobcategoriesplugin', primary_key=True, serialize=False, to='cms.CMSPlugin'),
        ),
        migrations.AlterField(
            model_name='joblistplugin',
            name='cmsplugin_ptr',
            field=models.OneToOneField(parent_link=True, related_name='aldryn_jobs_joblistplugin', primary_key=True, serialize=False, to='cms.CMSPlugin'),
        ),
        migrations.AlterField(
            model_name='joblistplugin',
            name='jobopenings',
            field=sortedm2m.fields.SortedManyToManyField(help_text='Choose specific Job Openings to show or leave empty to show latest. Note that Job Openings from different app configs will not appear.', to='aldryn_jobs.JobOpening', verbose_name='job openings', blank=True),
        ),
    ]
