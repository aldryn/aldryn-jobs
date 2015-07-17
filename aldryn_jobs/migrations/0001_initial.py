# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cms.models.fields
import app_data.fields
import sortedm2m.fields
from django.conf import settings
import djangocms_text_ckeditor.fields
import aldryn_jobs.models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20140926_2347'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('salutation', models.CharField(choices=[('male', 'Mr.'), ('female', 'Mrs.')], max_length=20, default='male', blank=True, verbose_name='Salutation')),
                ('first_name', models.CharField(max_length=20, verbose_name='First name')),
                ('last_name', models.CharField(max_length=20, verbose_name='Last name')),
                ('email', models.EmailField(max_length=75, verbose_name='E-mail')),
                ('cover_letter', models.TextField(blank=True, verbose_name='Cover letter')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('is_rejected', models.BooleanField(default=False, verbose_name='rejected?')),
                ('rejection_date', models.DateTimeField(null=True, blank=True, verbose_name='rejection date')),
            ],
            options={
                'verbose_name_plural': 'job applications',
                'ordering': ['-created'],
                'verbose_name': 'job application',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobApplicationAttachment',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('file', models.FileField(null=True, max_length=200, blank=True, upload_to=aldryn_jobs.models.default_jobs_attachment_upload_to)),
                ('application', models.ForeignKey(verbose_name='job application', related_name='attachments', to='aldryn_jobs.JobApplication')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobCategoriesPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(serialize=False, to='cms.CMSPlugin', parent_link=True, primary_key=True, auto_created=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='JobCategory',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('ordering', models.IntegerField(default=0, verbose_name='Ordering')),
            ],
            options={
                'verbose_name_plural': 'job categories',
                'ordering': ['ordering'],
                'verbose_name': 'job category',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobCategoryTranslation',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('language_code', models.CharField(max_length=15, db_index=True, verbose_name='Language')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('slug', models.SlugField(help_text='Auto-generated. Used in the URL. If changed, the URL will change. Clean it to have it re-created.', max_length=255, verbose_name='Slug', blank=True)),
                ('master', models.ForeignKey(null=True, related_name='translations', to='aldryn_jobs.JobCategory', editable=False)),
            ],
            options={
                'managed': True,
                'db_tablespace': '',
                'default_permissions': (),
                'verbose_name': 'job category Translation',
                'db_table': 'aldryn_jobs_jobcategory_translation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobListPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(serialize=False, to='cms.CMSPlugin', parent_link=True, primary_key=True, auto_created=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='JobOpening',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('publication_start', models.DateTimeField(null=True, blank=True, verbose_name='Published since')),
                ('publication_end', models.DateTimeField(null=True, blank=True, verbose_name='Published until')),
                ('can_apply', models.BooleanField(default=True, verbose_name='Viewer can apply for the job')),
                ('ordering', models.IntegerField(default=0, verbose_name='Ordering')),
                ('category', models.ForeignKey(verbose_name='category', related_name='jobs', to='aldryn_jobs.JobCategory')),
                ('content', cms.models.fields.PlaceholderField(null=True, to='cms.Placeholder', slotname='Job Opening Content', editable=False)),
            ],
            options={
                'verbose_name_plural': 'job openings',
                'ordering': ['ordering'],
                'verbose_name': 'job opening',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobOpeningTranslation',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('language_code', models.CharField(max_length=15, db_index=True, verbose_name='Language')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('slug', models.SlugField(help_text='Auto-generated. Used in the URL. If changed, the URL will change. Clean it to have it re-created.', max_length=255, verbose_name='Slug', blank=True)),
                ('lead_in', djangocms_text_ckeditor.fields.HTMLField(help_text='Will be displayed in lists', blank=True, verbose_name='Lead in')),
                ('master', models.ForeignKey(null=True, related_name='translations', to='aldryn_jobs.JobOpening', editable=False)),
            ],
            options={
                'managed': True,
                'db_tablespace': '',
                'default_permissions': (),
                'verbose_name': 'job opening Translation',
                'db_table': 'aldryn_jobs_jobopening_translation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobsConfig',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('type', models.CharField(max_length=100, verbose_name='type')),
                ('namespace', models.CharField(max_length=100, unique=True, verbose_name='instance namespace', default=None)),
                ('app_data', app_data.fields.AppDataField(default='{}', editable=False)),
                ('placeholder_jobs_detail_bottom', cms.models.fields.PlaceholderField(null=True, related_name='aldryn_jobs_detail_bottom', to='cms.Placeholder', slotname='jobs_detail_bottom', editable=False)),
                ('placeholder_jobs_detail_footer', cms.models.fields.PlaceholderField(null=True, related_name='aldryn_jobs_detail_footer', to='cms.Placeholder', slotname='jobs_detail_footer', editable=False)),
                ('placeholder_jobs_detail_top', cms.models.fields.PlaceholderField(null=True, related_name='aldryn_jobs_detail_top', to='cms.Placeholder', slotname='jobs_detail_top', editable=False)),
                ('placeholder_jobs_list_bottom', cms.models.fields.PlaceholderField(null=True, related_name='aldryn_jobs_list_bottom', to='cms.Placeholder', slotname='jobs_list_bottom', editable=False)),
                ('placeholder_jobs_list_top', cms.models.fields.PlaceholderField(null=True, related_name='aldryn_jobs_list_top', to='cms.Placeholder', slotname='jobs_list_top', editable=False)),
                ('placeholder_jobs_sidebar', cms.models.fields.PlaceholderField(null=True, related_name='aldryn_jobs_sidebar', to='cms.Placeholder', slotname='jobs_sidebar', editable=False)),
                ('placeholder_jobs_top', cms.models.fields.PlaceholderField(null=True, related_name='aldryn_jobs_top', to='cms.Placeholder', slotname='jobs_top', editable=False)),
            ],
            options={
                'verbose_name_plural': 'Aldryn Jobs configurations',
                'verbose_name': 'Aldryn Jobs configuration',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='jobopeningtranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AddField(
            model_name='joblistplugin',
            name='app_config',
            field=models.ForeignKey(null=True, verbose_name='app configuration', help_text='Select appropriate app. configuration for this plugin.', to='aldryn_jobs.JobsConfig'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='joblistplugin',
            name='jobopenings',
            field=sortedm2m.fields.SortedManyToManyField(null=True, blank=True, to='aldryn_jobs.JobOpening', verbose_name='job openings', help_text='Choose specific Job Openings to show or leave empty to show latest. Note that Job Openings from different app configs will not appear.'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='jobcategorytranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AddField(
            model_name='jobcategory',
            name='app_config',
            field=models.ForeignKey(null=True, verbose_name='app configuration', related_name='categories', to='aldryn_jobs.JobsConfig'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobcategory',
            name='supervisors',
            field=models.ManyToManyField(related_name='job_opening_categories', help_text='Those people will be notified via e-mail when new application arrives.', blank=True, to=settings.AUTH_USER_MODEL, verbose_name='supervisors'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobcategoriesplugin',
            name='app_config',
            field=models.ForeignKey(null=True, verbose_name='app configuration', help_text='Select appropriate app. configuration for this plugin.', to='aldryn_jobs.JobsConfig'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='job_opening',
            field=models.ForeignKey(related_name='applications', to='aldryn_jobs.JobOpening'),
            preserve_default=True,
        ),
    ]
