# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-02-05 20:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0019_attendance_att_hours'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together=set([('enrollment', 'attendance_date', 'att_hours')]),
        ),
    ]
