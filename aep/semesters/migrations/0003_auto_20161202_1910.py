# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-02 19:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('semesters', '0002_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day',
            name='semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='days', to='semesters.Semester'),
        ),
    ]