# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import app_data.fields
import djangocms_text_ckeditor.fields
import aldryn_jobs.models
import sortedm2m.fields
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20140926_2347'),
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('salutation', models.CharField(max_length=20, choices=[('male', 'Mr.'), ('female', 'Mrs.')], blank=True, default='male', verbose_name='Salutation')),
                ('first_name', models.CharField(max_length=20, verbose_name='First name')),
                ('last_name', models.CharField(max_length=20, verbose_name='Last name')),
                ('email', models.EmailField(max_length=75, verbose_name='E-mail')),
                ('cover_letter', models.TextField(blank=True, verbose_name='Cover letter')),
                ('created', models.DateTimeField(verbose_name='created', auto_now_add=True)),
                ('is_rejected', models.BooleanField(default=False, verbose_name='rejected?')),
                ('rejection_date', models.DateTimeField(verbose_name='rejection date', null=True, blank=True)),
            ],
            options={
                'ordering': ['-created'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobApplicationAttachment',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('file', models.FileField(upload_to=aldryn_jobs.models.default_jobs_attachment_upload_to, max_length=200, null=True, blank=True)),
                ('application', models.ForeignKey(related_name='attachments', to='aldryn_jobs.JobApplication')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobCategoriesPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(serialize=False, primary_key=True, auto_created=True, parent_link=True, to='cms.CMSPlugin')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='JobCategory',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('ordering', models.IntegerField(default=0, verbose_name='Ordering')),
            ],
            options={
                'ordering': ['ordering'],
                'verbose_name_plural': 'Job categories',
                'verbose_name': 'Job category',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobCategoryTranslation',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('language_code', models.CharField(max_length=15, db_index=True, verbose_name='Language')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('slug', models.SlugField(max_length=255, verbose_name='Slug', blank=True, help_text='Auto-generated. Used in the URL. If changed, the URL will change. Clean it to have it re-created.')),
                ('master', models.ForeignKey(null=True, related_name='translations', to='aldryn_jobs.JobCategory', editable=False)),
            ],
            options={
                'db_tablespace': '',
                'managed': True,
                'db_table': 'aldryn_jobs_jobcategory_translation',
                'default_permissions': (),
                'verbose_name': 'Job category Translation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobListPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(serialize=False, primary_key=True, auto_created=True, parent_link=True, to='cms.CMSPlugin')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='JobNewsletterRegistrationPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(serialize=False, primary_key=True, auto_created=True, parent_link=True, to='cms.CMSPlugin')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='JobOpening',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('publication_start', models.DateTimeField(verbose_name='Published since', null=True, blank=True)),
                ('publication_end', models.DateTimeField(verbose_name='Published until', null=True, blank=True)),
                ('can_apply', models.BooleanField(default=True, verbose_name='Viewer can apply for the job')),
                ('category', models.ForeignKey(related_name='jobs', to='aldryn_jobs.JobCategory', verbose_name='Category')),
                ('content', cms.models.fields.PlaceholderField(slotname='Job Opening Content', null=True, to='cms.Placeholder', editable=False)),
            ],
            options={
                'ordering': ['category__ordering', 'category', '-created'],
                'verbose_name_plural': 'Job openings',
                'verbose_name': 'Job opening',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobOpeningTranslation',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('language_code', models.CharField(max_length=15, db_index=True, verbose_name='Language')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('slug', models.SlugField(max_length=255, verbose_name='Slug', blank=True, help_text='Auto-generated. Used in the URL. If changed, the URL will change. Clean it to have it re-created.')),
                ('lead_in', djangocms_text_ckeditor.fields.HTMLField(help_text='Will be displayed in lists', blank=True, verbose_name='Lead in')),
                ('master', models.ForeignKey(null=True, related_name='translations', to='aldryn_jobs.JobOpening', editable=False)),
            ],
            options={
                'db_tablespace': '',
                'managed': True,
                'db_table': 'aldryn_jobs_jobopening_translation',
                'default_permissions': (),
                'verbose_name': 'Job opening Translation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobsConfig',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('type', models.CharField(max_length=100, verbose_name='type')),
                ('namespace', models.CharField(max_length=100, unique=True, default=None, verbose_name='instance namespace')),
                ('app_data', app_data.fields.AppDataField(default='{}', editable=False)),
                ('placeholder_jobs_detail_bottom', cms.models.fields.PlaceholderField(slotname='jobs_detail_bottom', null=True, related_name='aldryn_jobs_detail_bottom', to='cms.Placeholder', editable=False)),
                ('placeholder_jobs_detail_footer', cms.models.fields.PlaceholderField(slotname='jobs_detail_footer', null=True, related_name='aldryn_jobs_detail_footer', to='cms.Placeholder', editable=False)),
                ('placeholder_jobs_detail_top', cms.models.fields.PlaceholderField(slotname='jobs_detail_top', null=True, related_name='aldryn_jobs_detail_top', to='cms.Placeholder', editable=False)),
                ('placeholder_jobs_list_bottom', cms.models.fields.PlaceholderField(slotname='jobs_list_bottom', null=True, related_name='aldryn_jobs_list_bottom', to='cms.Placeholder', editable=False)),
                ('placeholder_jobs_list_top', cms.models.fields.PlaceholderField(slotname='jobs_list_top', null=True, related_name='aldryn_jobs_list_top', to='cms.Placeholder', editable=False)),
                ('placeholder_jobs_newsletter_registration', cms.models.fields.PlaceholderField(slotname='jobs_newsletter_registration', null=True, related_name='aldryn_jobs_newsletter_registration', to='cms.Placeholder', editable=False)),
                ('placeholder_jobs_sidebar', cms.models.fields.PlaceholderField(slotname='jobs_sidebar', null=True, related_name='aldryn_jobs_sidebar', to='cms.Placeholder', editable=False)),
                ('placeholder_jobs_top', cms.models.fields.PlaceholderField(slotname='jobs_top', null=True, related_name='aldryn_jobs_top', to='cms.Placeholder', editable=False)),
            ],
            options={
                'verbose_name_plural': 'Apphook configs',
                'verbose_name': 'Apphook config',
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NewsletterSignup',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('recipient', models.EmailField(max_length=75, unique=True, verbose_name='recipient')),
                ('default_language', models.CharField(max_length=32, choices=[('en', 'English'), ('de', 'German')], blank=True, default='', verbose_name='language')),
                ('signup_date', models.DateTimeField(auto_now_add=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('is_disabled', models.BooleanField(default=False)),
                ('confirmation_key', models.CharField(max_length=40, unique=True)),
                ('app_config', models.ForeignKey(null=True, to='aldryn_jobs.JobsConfig', verbose_name='app_config')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NewsletterSignupUser',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('signup', models.ForeignKey(related_name='related_user', to='aldryn_jobs.NewsletterSignup')),
                ('user', models.ForeignKey(related_name='newsletter_signup', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='jobsconfig',
            unique_together=set([('type', 'namespace')]),
        ),
        migrations.AlterUniqueTogether(
            name='jobopeningtranslation',
            unique_together=set([('language_code', 'master'), ('slug', 'language_code')]),
        ),
        migrations.AddField(
            model_name='jobnewsletterregistrationplugin',
            name='app_config',
            field=models.ForeignKey(null=True, help_text='Select appropriate add-on configuration for this plugin.', to='aldryn_jobs.JobsConfig', verbose_name='app_config'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobnewsletterregistrationplugin',
            name='mail_to_group',
            field=models.ManyToManyField(help_text='If user successfuly completed registration.<br/>Notification would be sent to users from selected groups<br/>Leave blank to disable notifications.<br/>', to='auth.Group', blank=True, verbose_name='Notification to'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='joblistplugin',
            name='app_config',
            field=models.ForeignKey(null=True, help_text='Select appropriate add-on configuration for this plugin.', to='aldryn_jobs.JobsConfig', verbose_name='app_config'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='joblistplugin',
            name='jobopenings',
            field=sortedm2m.fields.SortedManyToManyField(help_text="Select Job Openings to show or don't select any to show last job openings. Note that Job Openings form different app config would be ignored.", to='aldryn_jobs.JobOpening', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='jobcategorytranslation',
            unique_together=set([('language_code', 'master'), ('slug', 'language_code')]),
        ),
        migrations.AddField(
            model_name='jobcategory',
            name='app_config',
            field=models.ForeignKey(null=True, to='aldryn_jobs.JobsConfig', verbose_name='app_config'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobcategory',
            name='supervisors',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, help_text='Those people will be notified via e-mail when new application arrives.', related_name='job_opening_categories', blank=True, verbose_name='Supervisors'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobcategoriesplugin',
            name='app_config',
            field=models.ForeignKey(null=True, help_text='Select appropriate add-on configuration for this plugin.', to='aldryn_jobs.JobsConfig', verbose_name='app_config'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='job_opening',
            field=models.ForeignKey(to='aldryn_jobs.JobOpening'),
            preserve_default=True,
        ),
    ]
