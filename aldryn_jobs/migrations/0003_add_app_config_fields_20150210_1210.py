# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app_data.fields


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_jobs', '0002_auto_20150210_0240'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobsConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=100, verbose_name='type')),
                ('namespace', models.CharField(default=None, max_length=100, verbose_name='instance namespace')),
                ('app_data', app_data.fields.AppDataField(default=b'{}', editable=False)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Apphook config',
                'verbose_name_plural': 'Apphook configs',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='jobsconfig',
            unique_together=set([('type', 'namespace')]),
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='app_config',
            field=models.ForeignKey(verbose_name='app_config', to='aldryn_jobs.JobsConfig', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jobcategory',
            name='app_config',
            field=models.ForeignKey(verbose_name='app_config', to='aldryn_jobs.JobsConfig', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='joblistplugin',
            name='app_config',
            field=models.ForeignKey(verbose_name='app_config', to='aldryn_jobs.JobsConfig', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='joboffer',
            name='app_config',
            field=models.ForeignKey(verbose_name='app_config', to='aldryn_jobs.JobsConfig', null=True),
            preserve_default=True,
        ),
    ]
