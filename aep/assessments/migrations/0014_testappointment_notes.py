# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-05 16:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0013_auto_20170509_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='testappointment',
            name='notes',
            field=models.CharField(blank=True, max_length=140),
        ),
    ]