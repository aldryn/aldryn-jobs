# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app_data.fields
import djangocms_text_ckeditor.fields
from django.conf import settings
import cms.models.fields
import aldryn_jobs.models
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cms', '0003_auto_20140926_2347'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('salutation', models.CharField(verbose_name='salutation', max_length=20, choices=[('male', 'Mr.'), ('female', 'Mrs.')], blank=True, default='male')),
                ('first_name', models.CharField(verbose_name='first name', max_length=20)),
                ('last_name', models.CharField(verbose_name='last name', max_length=20)),
                ('email', models.EmailField(verbose_name='email', max_length=75)),
                ('cover_letter', models.TextField(verbose_name='cover letter', blank=True)),
                ('created', models.DateTimeField(verbose_name='created', auto_now_add=True)),
                ('is_rejected', models.BooleanField(verbose_name='rejected?', default=False)),
                ('rejection_date', models.DateTimeField(verbose_name='rejection date', blank=True, null=True)),
            ],
            options={
                'verbose_name': 'job application',
                'verbose_name_plural': 'job applications',
                'ordering': ['-created'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobApplicationAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('file', models.FileField(null=True, max_length=200, upload_to=aldryn_jobs.models.default_jobs_attachment_upload_to, blank=True)),
                ('application', models.ForeignKey(verbose_name='job application', related_name='attachments', to='aldryn_jobs.JobApplication')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobCategoriesPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='JobCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('ordering', models.IntegerField(verbose_name='ordering', default=0)),
            ],
            options={
                'verbose_name': 'job category',
                'verbose_name_plural': 'job categories',
                'ordering': ['ordering'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobCategoryTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('language_code', models.CharField(db_index=True, verbose_name='Language', max_length=15)),
                ('name', models.CharField(verbose_name='name', max_length=255)),
                ('slug', models.SlugField(verbose_name='slug', max_length=255, help_text='Auto-generated. Used in the URL. If changed, the URL will change. Clear it to have the slug re-created.', blank=True)),
                ('master', models.ForeignKey(null=True, related_name='translations', to='aldryn_jobs.JobCategory', editable=False)),
            ],
            options={
                'verbose_name': 'job category Translation',
                'default_permissions': (),
                'db_table': 'aldryn_jobs_jobcategory_translation',
                'db_tablespace': '',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobListPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, parent_link=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='JobOpening',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(verbose_name='active?', default=True)),
                ('publication_start', models.DateTimeField(verbose_name='published since', blank=True, null=True)),
                ('publication_end', models.DateTimeField(verbose_name='published until', blank=True, null=True)),
                ('can_apply', models.BooleanField(verbose_name='viewer can apply for the job?', default=True)),
                ('ordering', models.IntegerField(verbose_name='ordering', default=0)),
                ('category', models.ForeignKey(verbose_name='category', related_name='jobs', to='aldryn_jobs.JobCategory')),
                ('content', cms.models.fields.PlaceholderField(slotname='Job Opening Content', null=True, to='cms.Placeholder', editable=False)),
            ],
            options={
                'verbose_name': 'job opening',
                'verbose_name_plural': 'job openings',
                'ordering': ['ordering'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobOpeningTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('language_code', models.CharField(db_index=True, verbose_name='Language', max_length=15)),
                ('title', models.CharField(verbose_name='title', max_length=255)),
                ('slug', models.SlugField(db_index=False, verbose_name='slug', max_length=255, help_text='Auto-generated. Used in the URL. If changed, the URL will change. Clear it to have the slug re-created.', blank=True)),
                ('lead_in', djangocms_text_ckeditor.fields.HTMLField(verbose_name='short description', help_text='This text will be displayed in lists.', blank=True)),
                ('master', models.ForeignKey(null=True, related_name='translations', to='aldryn_jobs.JobOpening', editable=False)),
            ],
            options={
                'verbose_name': 'job opening Translation',
                'default_permissions': (),
                'db_table': 'aldryn_jobs_jobopening_translation',
                'db_tablespace': '',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobsConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('type', models.CharField(verbose_name='type', max_length=100)),
                ('namespace', models.CharField(verbose_name='instance namespace', max_length=100, default=None, unique=True)),
                ('app_data', app_data.fields.AppDataField(editable=False, default='{}')),
                ('placeholder_jobs_detail_bottom', cms.models.fields.PlaceholderField(slotname='jobs_detail_bottom', null=True, related_name='aldryn_jobs_detail_bottom', to='cms.Placeholder', editable=False)),
                ('placeholder_jobs_detail_footer', cms.models.fields.PlaceholderField(slotname='jobs_detail_footer', null=True, related_name='aldryn_jobs_detail_footer', to='cms.Placeholder', editable=False)),
                ('placeholder_jobs_detail_top', cms.models.fields.PlaceholderField(slotname='jobs_detail_top', null=True, related_name='aldryn_jobs_detail_top', to='cms.Placeholder', editable=False)),
                ('placeholder_jobs_list_bottom', cms.models.fields.PlaceholderField(slotname='jobs_list_bottom', null=True, related_name='aldryn_jobs_list_bottom', to='cms.Placeholder', editable=False)),
                ('placeholder_jobs_list_top', cms.models.fields.PlaceholderField(slotname='jobs_list_top', null=True, related_name='aldryn_jobs_list_top', to='cms.Placeholder', editable=False)),
                ('placeholder_jobs_sidebar', cms.models.fields.PlaceholderField(slotname='jobs_sidebar', null=True, related_name='aldryn_jobs_sidebar', to='cms.Placeholder', editable=False)),
                ('placeholder_jobs_top', cms.models.fields.PlaceholderField(slotname='jobs_top', null=True, related_name='aldryn_jobs_top', to='cms.Placeholder', editable=False)),
            ],
            options={
                'verbose_name': 'Aldryn Jobs configuration',
                'verbose_name_plural': 'Aldryn Jobs configurations',
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
            field=models.ForeignKey(verbose_name='app configuration', help_text='Select appropriate app. configuration for this plugin.', null=True, to='aldryn_jobs.JobsConfig'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='joblistplugin',
            name='jobopenings',
            field=sortedm2m.fields.SortedManyToManyField(verbose_name='job openings', to='aldryn_jobs.JobOpening', help_text='Choose specific Job Openings to show or leave empty to show latest. Note that Job Openings from different app configs will not appear.', blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='jobcategorytranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AddField(
            model_name='jobcategory',
            name='app_config',
            field=models.ForeignKey(verbose_name='app configuration', null=True, related_name='categories', to='aldryn_jobs.JobsConfig'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobcategory',
            name='supervisors',
            field=models.ManyToManyField(verbose_name='supervisors', to=settings.AUTH_USER_MODEL, help_text='Supervisors will be notified via email when a new job application arrives.', blank=True, related_name='job_opening_categories'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobcategoriesplugin',
            name='app_config',
            field=models.ForeignKey(verbose_name='app configuration', help_text='Select appropriate app. configuration for this plugin.', null=True, to='aldryn_jobs.JobsConfig'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='job_opening',
            field=models.ForeignKey(to='aldryn_jobs.JobOpening', related_name='applications'),
            preserve_default=True,
        ),
    ]
