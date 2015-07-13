# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0012_auto_20150607_2207'),
        ('aldryn_jobs', '0011_remove_joboffer_app_config'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobsconfig',
            name='placeholder_jobs_detail_bottom',
            field=cms.models.fields.PlaceholderField(related_name='aldryn_jobs_detail_bottom', slotname='jobs_detail_bottom', editable=False, to='cms.Placeholder', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobsconfig',
            name='placeholder_jobs_detail_footer',
            field=cms.models.fields.PlaceholderField(related_name='aldryn_jobs_detail_footer', slotname='jobs_detail_footer', editable=False, to='cms.Placeholder', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobsconfig',
            name='placeholder_jobs_detail_top',
            field=cms.models.fields.PlaceholderField(related_name='aldryn_jobs_detail_top', slotname='jobs_detail_top', editable=False, to='cms.Placeholder', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobsconfig',
            name='placeholder_jobs_list_bottom',
            field=cms.models.fields.PlaceholderField(related_name='aldryn_jobs_list_bottom', slotname='jobs_list_bottom', editable=False, to='cms.Placeholder', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobsconfig',
            name='placeholder_jobs_list_top',
            field=cms.models.fields.PlaceholderField(related_name='aldryn_jobs_list_top', slotname='jobs_list_top', editable=False, to='cms.Placeholder', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobsconfig',
            name='placeholder_jobs_newsletter_registration',
            field=cms.models.fields.PlaceholderField(related_name='aldryn_jobs_newsletter_registration', slotname='jobs_newsletter_registration', editable=False, to='cms.Placeholder', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobsconfig',
            name='placeholder_jobs_sidebar',
            field=cms.models.fields.PlaceholderField(related_name='aldryn_jobs_sidebar', slotname='jobs_sidebar', editable=False, to='cms.Placeholder', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobsconfig',
            name='placeholder_jobs_top',
            field=cms.models.fields.PlaceholderField(related_name='aldryn_jobs_top', slotname='jobs_top', editable=False, to='cms.Placeholder', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='newslettersignup',
            name='default_language',
            field=models.CharField(default='', max_length=32, verbose_name='language', blank=True, choices=[(b'en', 'English'), (b'de', 'Deutsch')]),
            preserve_default=True,
        ),
    ]
