# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-01 22:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0011_auto_20161230_0107'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attendance',
            options={'ordering': ['attendance_date']},
        ),
        migrations.AlterField(
            model_name='attendance',
            name='time_in',
            field=models.TimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='time_out',
            field=models.TimeField(blank=True),
        ),
    ]