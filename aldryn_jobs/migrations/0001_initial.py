# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import aldryn_jobs.models
import cms.models.fields
from django.conf import settings
import djangocms_text_ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20140926_2347'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('salutation', models.CharField(default=b'male', max_length=20, verbose_name='Salutation', blank=True, choices=[(b'male', 'Mr.'), (b'female', 'Mrs.')])),
                ('first_name', models.CharField(max_length=20, verbose_name='First name')),
                ('last_name', models.CharField(max_length=20, verbose_name='Last name')),
                ('email', models.EmailField(max_length=75, verbose_name='E-mail')),
                ('cover_letter', models.TextField(verbose_name='Cover letter', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('is_rejected', models.BooleanField(default=False, verbose_name='Rejected')),
                ('rejection_date', models.DateTimeField(null=True, verbose_name='Rejection date', blank=True)),
            ],
            options={
                'ordering': ['-created'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobApplicationAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(max_length=200, null=True, upload_to=aldryn_jobs.models.default_jobs_attachment_upload_to, blank=True)),
                ('application', models.ForeignKey(related_name='attachments', to='aldryn_jobs.JobApplication')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ordering', models.IntegerField(default=0, verbose_name='Ordering')),
                ('supervisors', models.ManyToManyField(help_text='Those people will be notified via e-mail when new application arrives.', related_name='job_offer_categories', verbose_name='Supervisors', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'ordering': ['ordering'],
                'verbose_name': 'Job category',
                'verbose_name_plural': 'Job categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobCategoryTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('slug', models.SlugField(help_text='Auto-generated. Used in the URL. If changed, the URL will change. Clean it to have it re-created.', max_length=255, verbose_name='Slug', blank=True)),
                ('language_code', models.CharField(max_length=15, db_index=True)),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='aldryn_jobs.JobCategory', null=True)),
            ],
            options={
                'abstract': False,
                'db_table': 'aldryn_jobs_jobcategory_translation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobListPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='JobOffer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('publication_start', models.DateTimeField(null=True, verbose_name='Published since', blank=True)),
                ('publication_end', models.DateTimeField(null=True, verbose_name='Published until', blank=True)),
                ('can_apply', models.BooleanField(default=True, verbose_name='Viewer can apply for the job')),
                ('category', models.ForeignKey(related_name='jobs', verbose_name='Category', to='aldryn_jobs.JobCategory')),
                ('content', cms.models.fields.PlaceholderField(slotname=b'Job Offer Content', editable=False, to='cms.Placeholder', null=True)),
            ],
            options={
                'ordering': ['category__ordering', 'category', '-created'],
                'verbose_name': 'Job offer',
                'verbose_name_plural': 'Job offers',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JobOfferTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('slug', models.SlugField(help_text='Auto-generated. Used in the URL. If changed, the URL will change. Clean it to have it re-created.', max_length=255, verbose_name='Slug', blank=True)),
                ('lead_in', djangocms_text_ckeditor.fields.HTMLField(help_text='Will be displayed in lists', verbose_name='Lead in', blank=True)),
                ('language_code', models.CharField(max_length=15, db_index=True)),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='aldryn_jobs.JobOffer', null=True)),
            ],
            options={
                'abstract': False,
                'db_table': 'aldryn_jobs_joboffer_translation',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='joboffertranslation',
            unique_together=set([('language_code', 'master'), ('slug', 'language_code')]),
        ),
        migrations.AlterUniqueTogether(
            name='jobcategorytranslation',
            unique_together=set([('language_code', 'master'), ('slug', 'language_code')]),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='job_offer',
            field=models.ForeignKey(to='aldryn_jobs.JobOffer'),
            preserve_default=True,
        ),
    ]
