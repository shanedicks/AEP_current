# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-09 01:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0009_auto_20161208_1928'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='room',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
