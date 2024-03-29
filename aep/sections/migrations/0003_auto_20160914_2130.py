# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-15 02:30
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0002_auto_20160911_2119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='WRU_ID',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='section',
            name='end_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='section',
            name='seats',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='section',
            name='semester',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sections.Semester'),
        ),
        migrations.AlterField(
            model_name='section',
            name='start_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='section',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='teacher_classes', to=settings.AUTH_USER_MODEL),
        ),
    ]
