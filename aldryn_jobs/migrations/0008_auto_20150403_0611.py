# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import aldryn_categories.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('aldryn_categories', '0003_auto_20150128_1359'),
        ('aldryn_jobs', '0007_auto_20150330_0545'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobCategoryOpts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('app_config', models.ForeignKey(verbose_name='app_config', to='aldryn_jobs.JobsConfig', null=True)),
                ('category', aldryn_categories.fields.CategoryOneToOneField(related_name='jobs_opts', to='aldryn_categories.Category')),
                ('supervisors', models.ManyToManyField(help_text='Those people will be notified via e-mail when new application arrives.', related_name='job_categories_opts', verbose_name='Supervisors', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'verbose_name': 'Job category opts',
                'verbose_name_plural': 'Job categories opts',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='joboffer',
            name='category_new',
            field=aldryn_categories.fields.CategoryForeignKey(related_name='job_offers', default=None, to='aldryn_categories.Category', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='joboffer',
            name='category',
            field=models.ForeignKey(related_name='jobs', default=None, verbose_name='Category', to='aldryn_jobs.JobCategory', null=True),
            preserve_default=True,
        ),
    ]
