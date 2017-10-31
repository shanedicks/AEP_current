# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-20 18:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0015_auto_20170705_1423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tabe',
            name='lang_level',
            field=models.CharField(choices=[('A', 'A'), ('D', 'D'), ('M', 'M'), ('E', 'E'), ('L', 'L')], max_length=1),
        ),
        migrations.AlterField(
            model_name='tabe',
            name='math_level',
            field=models.CharField(choices=[('A', 'A'), ('D', 'D'), ('M', 'M'), ('E', 'E'), ('L', 'L')], max_length=1),
        ),
        migrations.AlterField(
            model_name='tabe',
            name='read_level',
            field=models.CharField(choices=[('A', 'A'), ('D', 'D'), ('M', 'M'), ('E', 'E'), ('L', 'L')], max_length=1),
        ),
    ]