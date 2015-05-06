# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('aldryn_categories', '0004_auto_20150331_1701'),
        ('aldryn_jobs', '0007_auto_20150330_0545'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobCategoryNew',
            fields=[
                ('category_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='aldryn_categories.Category')),
                ('ordering', models.IntegerField(default=0, verbose_name='Ordering')),
                ('app_config', models.ForeignKey(verbose_name='app_config', to='aldryn_jobs.JobsConfig', null=True)),
                ('supervisors', models.ManyToManyField(help_text='Those people will be notified via e-mail when new application arrives.', related_name='job_offer_categories_new', verbose_name='Supervisors', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'ordering': ['ordering'],
                'verbose_name': 'Job category new',
                'verbose_name_plural': 'Job categories new',
            },
            bases=('aldryn_categories.category',),
        ),
    ]
