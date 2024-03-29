# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-15 03:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0029_auto_20170503_1300'),
        ('coaching', '0006_auto_20170608_2152'),
    ]

    operations = [
        migrations.CreateModel(
            name='ElearnRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('elearn_status', models.CharField(blank=True, choices=[('Active', 'Active'), ('InActive', 'InActive'), ('Completed', 'Completed')], max_length=9)),
                ('status_updated', models.DateField(blank=True, null=True)),
                ('intake_date', models.DateField(blank=True, null=True)),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='elearn_record', to='people.Student')),
            ],
        ),
    ]
