# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-25 17:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0012_auto_20160925_1220'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wioa',
            old_name='emotional_distubance',
            new_name='emotional_disturbance',
        ),
    ]
