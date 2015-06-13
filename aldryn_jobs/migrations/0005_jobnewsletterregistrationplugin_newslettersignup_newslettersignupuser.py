# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('cms', '__latest__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('aldryn_jobs', '0004_data_create_default_namespace_20150210_1211'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobNewsletterRegistrationPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('mail_to_group', models.ManyToManyField(to='auth.Group', verbose_name='Signup notification to')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='NewsletterSignup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('recipient', models.EmailField(unique=True, max_length=75, verbose_name='Recipient')),
                ('default_language', models.CharField(default=b'', max_length=32, verbose_name='Language', blank=True, choices=[(b'en', b'en'), (b'de', b'de')])),
                ('signup_date', models.DateTimeField(auto_now_add=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('is_disabled', models.BooleanField(default=False)),
                ('confirmation_key', models.CharField(unique=True, max_length=40)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NewsletterSignupUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('signup', models.ForeignKey(related_name='related_user', to='aldryn_jobs.NewsletterSignup')),
                ('user', models.ForeignKey(related_name='newsletter_signup', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
