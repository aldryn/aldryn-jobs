 # -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_jobs', '0005_jobnewsletterregistrationplugin_newslettersignup_newslettersignupuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='joblistplugin',
            name='joboffers',
            field=sortedm2m.fields.SortedManyToManyField(help_text="Select Job Offers to show or don't select any to show lasted job offers.", to='aldryn_jobs.JobOffer', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='joblistplugin',
            name='num_entries',
            field=models.PositiveSmallIntegerField(default=25, help_text='The number of entries to be displayed. Default is 25. Only apply when any Job Offers are selected.', verbose_name='Number of entries'),
            preserve_default=True,
        ),
    ]
