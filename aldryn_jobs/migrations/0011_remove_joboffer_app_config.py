# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_jobs', '0010_auto_20150711_1550'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='joboffer',
            name='app_config',
        ),
    ]
