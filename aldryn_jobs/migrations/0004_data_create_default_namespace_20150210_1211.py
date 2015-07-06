# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, transaction
from django.db.models import get_model
from django.db.utils import ProgrammingError

def create_default_namespaces(apps, schema_editor):

    JobsConfig = apps.get_model('aldryn_jobs', 'JobsConfig')
    models = [apps.get_model('aldryn_jobs', 'JobCategory'),
              apps.get_model('aldryn_jobs', 'JobOffer'),
              apps.get_model('aldryn_jobs', 'JobApplication'),
              apps.get_model('aldryn_jobs', 'JobListPlugin'), ]

    ns, created = JobsConfig.objects.get_or_create(namespace='aldryn_jobs')

    for model in models:
        # if cms migrations migrated to latest and after that we will try to
        # migrate this - we would get an exception because apps.get_model
        # contains cms models at point of dependency migration
        # so if that is the case - import latest model.
        try:
            # to avoid the following error:
            #   django.db.utils.InternalError: current transaction is aborted,
            #   commands ignored until end of transaction block
            # we need to cleanup or avoid that by making them atomic.
            with transaction.atomic():
                model_objects = list(model.objects.filter(app_config__isnull=True))
        except ProgrammingError:
            new_model = get_model('aldryn_jobs.{0}'.format(model.__name__))
            with transaction.atomic():
                model_objects = new_model.objects.filter(app_config__isnull=True)
        for entry in model_objects:
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
