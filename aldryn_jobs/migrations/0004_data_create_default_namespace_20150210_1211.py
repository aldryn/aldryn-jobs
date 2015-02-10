# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def create_default_namespaces(apps, schema_editor):
    JobsConfig = apps.get_model('aldryn_jobs', 'JobsConfig')
    models = [apps.get_model('aldryn_jobs', 'JobCategory'),
              apps.get_model('aldryn_jobs', 'JobOffer'),
              apps.get_model('aldryn_jobs', 'JobApplication'),
              apps.get_model('aldryn_jobs', 'JobListPlugin'),]

    ns, created = JobsConfig.objects.get_or_create(namespace='aldryn_jobs')

    for model in models:
        for entry in model.objects.filter(app_config__isnull=True):
            entry.app_config = ns
            entry.save()

def remove_namespaces(apps, schema_editor):
    JobsConfig = apps.get_model('aldryn_jobs', 'JobsConfig')
    JobsConfig.objects.filter(namespace='aldryn_jobs').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_jobs', '0003_add_app_config_fields_20150210_1210'),
    ]

    operations = [
        migrations.RunPython(create_default_namespaces, remove_namespaces),
    ]
