# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-16 21:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('people', '0025_auto_20170216_2043'),
    ]

    operations = [
        migrations.AddField(
            model_name='collegeinterest',
            name='creator',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='college_interest_records', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='collegeinterest',
            name='aid_status',
            field=models.CharField(blank=True, choices=[('D', 'Default'), ('R', 'Repayment'), ('P', 'Paid in full'), ('U', "I don't know"), ('O', 'Other')], max_length=1, verbose_name='If you have used financial aid before, what is your current financial aid status?'),
        ),
        migrations.AlterField(
            model_name='collegeinterest',
            name='financial_aid',
            field=models.CharField(blank=True, choices=[('Y', 'Yes'), ('N', 'No'), ('C', "I don't know")], max_length=1, verbose_name='Have you ever used financial aid (student loans or grants) before?'),
        ),
        migrations.AlterField(
            model_name='collegeinterest',
            name='prev_balance',
            field=models.CharField(blank=True, choices=[('Y', 'Yes'), ('N', 'No'), ('C', "I don't know")], max_length=1, verbose_name="If you've attended college before, do you owe a balance to that college?"),
        ),
    ]
