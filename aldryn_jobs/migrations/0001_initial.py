# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sortedm2m.fields
import app_data.fields
import cms.models.fields
import djangocms_text_ckeditor.fields
import aldryn_jobs.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cms', '0012_auto_20150607_2207'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('salutation', models.CharField(choices=[('male', 'Mr.'), ('female', 'Mrs.')], verbose_name='Salutation', blank=True, max_length=20, default='male')),
                ('first_name', models.CharField(max_length=20, verbose_name='First name')),
                ('last_name', models.CharField(max_length=20, verbose_name='Last name')),
                ('email', models.EmailField(max_length=75, verbose_name='E-mail')),
                ('cover_letter', models.TextField(blank=True, verbose_name='Cover letter')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('is_rejected', models.BooleanField(verbose_name='rejected?', default=False)),
                ('rejection_date', models.DateTimeField(blank=True, verbose_name='rejection date', null=True)),
            ],
            options={
                'ordering': ['-created'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobApplicationAttachment',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('file', models.FileField(blank=True, max_length=200, upload_to=aldryn_jobs.models.default_jobs_attachment_upload_to, null=True)),
                ('application', models.ForeignKey(related_name='attachments', to='aldryn_jobs.JobApplication')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobCategoriesPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(primary_key=True, serialize=False, to='cms.CMSPlugin', auto_created=True, parent_link=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='JobCategory',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('ordering', models.IntegerField(verbose_name='Ordering', default=0)),
            ],
            options={
                'verbose_name': 'Job category',
                'ordering': ['ordering'],
                'verbose_name_plural': 'Job categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobCategoryTranslation',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('slug', models.SlugField(max_length=255, verbose_name='Slug', blank=True, help_text='Auto-generated. Used in the URL. If changed, the URL will change. Clean it to have it re-created.')),
                ('master', models.ForeignKey(related_name='translations', null=True, editable=False, to='aldryn_jobs.JobCategory')),
            ],
            options={
                'db_tablespace': '',
                'verbose_name': 'Job category Translation',
                'db_table': 'aldryn_jobs_jobcategory_translation',
                'managed': True,
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobListPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(primary_key=True, serialize=False, to='cms.CMSPlugin', auto_created=True, parent_link=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='JobNewsletterRegistrationPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(primary_key=True, serialize=False, to='cms.CMSPlugin', auto_created=True, parent_link=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='JobOpening',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(verbose_name='Active', default=True)),
                ('publication_start', models.DateTimeField(blank=True, verbose_name='Published since', null=True)),
                ('publication_end', models.DateTimeField(blank=True, verbose_name='Published until', null=True)),
                ('can_apply', models.BooleanField(verbose_name='Viewer can apply for the job', default=True)),
                ('category', models.ForeignKey(related_name='jobs', to='aldryn_jobs.JobCategory', verbose_name='Category')),
                ('content', cms.models.fields.PlaceholderField(to='cms.Placeholder', null=True, slotname='Job Offer Content', editable=False)),
            ],
            options={
                'verbose_name': 'Job offer',
                'ordering': ['category__ordering', 'category', '-created'],
                'verbose_name_plural': 'Job offers',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobOpeningTranslation',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('slug', models.SlugField(max_length=255, verbose_name='Slug', blank=True, help_text='Auto-generated. Used in the URL. If changed, the URL will change. Clean it to have it re-created.')),
                ('lead_in', djangocms_text_ckeditor.fields.HTMLField(blank=True, verbose_name='Lead in', help_text='Will be displayed in lists')),
                ('master', models.ForeignKey(related_name='translations', null=True, editable=False, to='aldryn_jobs.JobOpening')),
            ],
            options={
                'db_tablespace': '',
                'verbose_name': 'Job offer Translation',
                'db_table': 'aldryn_jobs_jobopening_translation',
                'managed': True,
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobsConfig',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('type', models.CharField(max_length=100, verbose_name='type')),
                ('namespace', models.CharField(unique=True, verbose_name='instance namespace', max_length=100, default=None)),
                ('app_data', app_data.fields.AppDataField(editable=False, default='{}')),
                ('placeholder_jobs_detail_bottom', cms.models.fields.PlaceholderField(related_name='aldryn_jobs_detail_bottom', null=True, slotname='jobs_detail_bottom', editable=False, to='cms.Placeholder')),
                ('placeholder_jobs_detail_footer', cms.models.fields.PlaceholderField(related_name='aldryn_jobs_detail_footer', null=True, slotname='jobs_detail_footer', editable=False, to='cms.Placeholder')),
                ('placeholder_jobs_detail_top', cms.models.fields.PlaceholderField(related_name='aldryn_jobs_detail_top', null=True, slotname='jobs_detail_top', editable=False, to='cms.Placeholder')),
                ('placeholder_jobs_list_bottom', cms.models.fields.PlaceholderField(related_name='aldryn_jobs_list_bottom', null=True, slotname='jobs_list_bottom', editable=False, to='cms.Placeholder')),
                ('placeholder_jobs_list_top', cms.models.fields.PlaceholderField(related_name='aldryn_jobs_list_top', null=True, slotname='jobs_list_top', editable=False, to='cms.Placeholder')),
                ('placeholder_jobs_newsletter_registration', cms.models.fields.PlaceholderField(related_name='aldryn_jobs_newsletter_registration', null=True, slotname='jobs_newsletter_registration', editable=False, to='cms.Placeholder')),
                ('placeholder_jobs_sidebar', cms.models.fields.PlaceholderField(related_name='aldryn_jobs_sidebar', null=True, slotname='jobs_sidebar', editable=False, to='cms.Placeholder')),
                ('placeholder_jobs_top', cms.models.fields.PlaceholderField(related_name='aldryn_jobs_top', null=True, slotname='jobs_top', editable=False, to='cms.Placeholder')),
            ],
            options={
                'verbose_name': 'Apphook config',
                'abstract': False,
                'verbose_name_plural': 'Apphook configs',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NewsletterSignup',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('recipient', models.EmailField(unique=True, max_length=75, verbose_name='recipient')),
                ('default_language', models.CharField(choices=[('en', 'English'), ('de', 'German')], verbose_name='language', blank=True, max_length=32, default='')),
                ('signup_date', models.DateTimeField(auto_now_add=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('is_disabled', models.BooleanField(default=False)),
                ('confirmation_key', models.CharField(unique=True, max_length=40)),
                ('app_config', models.ForeignKey(to='aldryn_jobs.JobsConfig', null=True, verbose_name='app_config')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NewsletterSignupUser',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
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
            field=models.ForeignKey(to='aldryn_jobs.JobsConfig', null=True, verbose_name='app_config', help_text='Select appropriate add-on configuration for this plugin.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobnewsletterregistrationplugin',
            name='mail_to_group',
            field=models.ManyToManyField(to='auth.Group', blank=True, verbose_name='Notification to', help_text='If user successfuly completed registration.<br/>Notification would be sent to users from selected groups<br/>Leave blank to disable notifications.<br/>'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='joblistplugin',
            name='app_config',
            field=models.ForeignKey(to='aldryn_jobs.JobsConfig', null=True, verbose_name='app_config', help_text='Select appropriate add-on configuration for this plugin.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='joblistplugin',
            name='joboffers',
            field=sortedm2m.fields.SortedManyToManyField(to='aldryn_jobs.JobOpening', blank=True, help_text="Select Job Offers to show or don't select any to show last job offers. Note that Job Offers form different app config would be ignored.", null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='jobcategorytranslation',
            unique_together=set([('language_code', 'master'), ('slug', 'language_code')]),
        ),
        migrations.AddField(
            model_name='jobcategory',
            name='app_config',
            field=models.ForeignKey(to='aldryn_jobs.JobsConfig', null=True, verbose_name='app_config'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobcategory',
            name='supervisors',
            field=models.ManyToManyField(related_name='job_offer_categories', to=settings.AUTH_USER_MODEL, blank=True, verbose_name='Supervisors', help_text='Those people will be notified via e-mail when new application arrives.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobcategoriesplugin',
            name='app_config',
            field=models.ForeignKey(to='aldryn_jobs.JobsConfig', null=True, verbose_name='app_config', help_text='Select appropriate add-on configuration for this plugin.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='job_offer',
            field=models.ForeignKey(to='aldryn_jobs.JobOpening'),
            preserve_default=True,
        ),
    ]
