# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-02 19:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0006_auto_20161019_1403'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='program',
            field=models.CharField(blank=True, choices=[('ESL', 'ESL'), ('CCR', 'CCR'), ('TRANS', 'Transitions')], max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='section',
            name='site',
            field=models.CharField(blank=True, choices=[('CP', 'City Park'), ('MC', 'NOALC'), ('WB', 'West Bank'), ('JP', 'Jefferson Parish'), ('SC', 'Sidney Collier')], max_length=2),
        ),
    ]
