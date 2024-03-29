# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-20 17:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coaching', '0009_auto_20170814_2312'),
    ]

    operations = [
        migrations.AddField(
            model_name='elearnrecord',
            name='g_suite_email',
            field=models.EmailField(blank=True, max_length=40),
        ),
        migrations.AlterField(
            model_name='elearnrecord',
            name='elearn_status',
            field=models.CharField(blank=True, choices=[('Applicant', 'Applicant'), ('Pending', 'Pending'), ('On Hold', 'On Hold'), ('Active', 'Active')], default='Applicant', max_length=9),
        ),
    ]
