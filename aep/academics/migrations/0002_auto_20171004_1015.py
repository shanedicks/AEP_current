# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-10-04 17:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='skill',
            name='ccrs',
        ),
        migrations.AddField(
            model_name='course',
            name='g_suite_id',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='resource',
            name='link',
            field=models.URLField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='skill',
            name='standard',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
