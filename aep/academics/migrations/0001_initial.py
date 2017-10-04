# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-27 06:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60)),
                ('code', models.CharField(blank=True, max_length=6)),
                ('description', models.TextField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('ccrs', models.CharField(blank=True, max_length=12)),
                ('description', models.TextField(blank=True, max_length=1000)),
                ('resources', models.ManyToManyField(to='academics.Resource')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='resources',
            field=models.ManyToManyField(to='academics.Resource'),
        ),
        migrations.AddField(
            model_name='course',
            name='skills',
            field=models.ManyToManyField(to='academics.Skill'),
        ),
    ]
