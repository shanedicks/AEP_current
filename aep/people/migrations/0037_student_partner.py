# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-21 23:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0036_auto_20180117_2146'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='partner',
            field=models.CharField(blank=True, max_length=40),
        ),
    ]
