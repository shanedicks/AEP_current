# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-18 19:09
from __future__ import unicode_literals

import core.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0006_auto_20160917_1343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='AEP_ID',
            field=models.CharField(default=core.utils.make_AEP_ID, max_length=8, unique=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='WRU_ID',
            field=models.CharField(blank=True, max_length=7, null=True),
        ),
    ]
