# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_jobs', '0006_auto_20150330_0111'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobCategoriesPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('app_config', models.ForeignKey(verbose_name='app_config', to='aldryn_jobs.JobsConfig', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.RemoveField(
            model_name='joblistplugin',
            name='num_entries',
        ),
        migrations.AlterField(
            model_name='joblistplugin',
            name='joboffers',
            field=sortedm2m.fields.SortedManyToManyField(help_text="Select Job Offers to show or don't select any to show last job offers.", to='aldryn_jobs.JobOffer', null=True, blank=True),
            preserve_default=True,
        ),
    ]
