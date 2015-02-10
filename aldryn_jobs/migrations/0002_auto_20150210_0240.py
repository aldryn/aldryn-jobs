# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_jobs', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jobcategorytranslation',
            options={'default_permissions': (), 'verbose_name': 'Job category Translation'},
        ),
        migrations.AlterModelOptions(
            name='joboffertranslation',
            options={'default_permissions': (), 'verbose_name': 'Job offer Translation'},
        ),
        migrations.AlterField(
            model_name='jobcategorytranslation',
            name='language_code',
            field=models.CharField(db_index=True, max_length=15, verbose_name='Language', choices=[(b'en', b'en'), (b'de', b'de')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='joboffertranslation',
            name='language_code',
            field=models.CharField(db_index=True, max_length=15, verbose_name='Language', choices=[(b'en', b'en'), (b'de', b'de')]),
            preserve_default=True,
        ),
    ]
