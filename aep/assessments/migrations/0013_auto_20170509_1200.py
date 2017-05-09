# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-09 16:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assessments', '0012_auto_20170508_1318'),
    ]

    operations = [
        migrations.AddField(
            model_name='hiset_practice',
            name='proctor',
            field=models.CharField(choices=[('Staff', 'Proctored by Staff Member'), ('Self', 'Self-Administered')], default='Staff', max_length=5),
        ),
        migrations.AddField(
            model_name='hiset_practice',
            name='reported_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='hpt_submissions', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hiset_practice',
            name='test_version',
            field=models.CharField(blank=True, choices=[('FPT2', 'Free Practice Test 2 (2015)'), ('FPT3', 'Free Practice Test 3 (2015)'), ('PPT2', 'Paid Practice Test 2 (2015)'), ('PPT3', 'Paid Practice Test 3 (2015)'), ('PPT4', 'Paid Practice Test 4 (2015)'), ('PPT5', 'Paid Practice Test 5 (2015)'), ('OPT2', 'Official Practice Test 2 (2015)'), ('OPT3', 'Official Practice Test 3 (2015)'), ('FPT6A', 'Free Practice Test 6A (2016)'), ('PPT6A', 'Paid Practice Test 6A (2016)'), ('OPT6A', 'Official Practice Test 6A (2016)')], max_length=5),
        ),
    ]
