# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-02 19:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0018_auto_20161019_2120'),
        ('sections', '0007_auto_20161202_1910'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='enrollment',
            unique_together=set([('student', 'section')]),
        ),
    ]