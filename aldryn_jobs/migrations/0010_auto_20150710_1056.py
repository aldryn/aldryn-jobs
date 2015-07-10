# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_newsblog', '0004_auto_20150622_1606'),
        ('aldryn_categories', '0004_auto_20150623_0859'),
        ('cms', '0003_auto_20140926_2347'),
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
            options={'default_permissions': (), 'verbose_name': 'Job category Translation', 'managed': True},
        ),
        migrations.AlterModelOptions(
            name='joboffertranslation',
            options={'default_permissions': (), 'verbose_name': 'Job offer Translation', 'managed': True},
        ),
        migrations.AlterModelOptions(
            name='jobsconfig',
            options={},
        ),
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
            model_name='newslettersignup',
            name='default_language',
            field=models.CharField(default=b'', max_length=32, verbose_name='Language', blank=True, choices=[(b'en', 'English'), (b'de', 'Deutsch')]),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='jobsconfig',
            unique_together=set([]),
        ),
    ]
