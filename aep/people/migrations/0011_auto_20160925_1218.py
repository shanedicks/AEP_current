# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-25 17:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0010_auto_20160920_1656'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wioa',
            name='disability_1',
        ),
        migrations.RemoveField(
            model_name='wioa',
            name='disability_10',
        ),
        migrations.RemoveField(
            model_name='wioa',
            name='disability_11',
        ),
        migrations.RemoveField(
            model_name='wioa',
            name='disability_12',
        ),
        migrations.RemoveField(
            model_name='wioa',
            name='disability_13',
        ),
        migrations.RemoveField(
            model_name='wioa',
            name='disability_14',
        ),
        migrations.RemoveField(
            model_name='wioa',
            name='disability_15',
        ),
        migrations.RemoveField(
            model_name='wioa',
            name='disability_2',
        ),
        migrations.RemoveField(
            model_name='wioa',
            name='disability_3',
        ),
        migrations.RemoveField(
            model_name='wioa',
            name='disability_4',
        ),
        migrations.RemoveField(
            model_name='wioa',
            name='disability_5',
        ),
        migrations.RemoveField(
            model_name='wioa',
            name='disability_6',
        ),
        migrations.RemoveField(
            model_name='wioa',
            name='disability_7',
        ),
        migrations.RemoveField(
            model_name='wioa',
            name='disability_8',
        ),
        migrations.RemoveField(
            model_name='wioa',
            name='disability_9',
        ),
        migrations.RemoveField(
            model_name='wioa',
            name='dislearning_1',
        ),
        migrations.RemoveField(
            model_name='wioa',
            name='dislearning_2',
        ),
        migrations.RemoveField(
            model_name='wioa',
            name='dislearning_3',
        ),
        migrations.RemoveField(
            model_name='wioa',
            name='dislearning_4',
        ),
        migrations.AddField(
            model_name='wioa',
            name='adhd',
            field=models.BooleanField(default=False, verbose_name='ADHD'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='autism',
            field=models.BooleanField(default=False, verbose_name='Autism'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='deaf',
            field=models.BooleanField(default=False, verbose_name='Deafness'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='deaf_blind',
            field=models.BooleanField(default=False, verbose_name='Deaf-blindness'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='dyscalculia',
            field=models.BooleanField(default=False, verbose_name='Dyscalculia'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='dysgraphia',
            field=models.BooleanField(default=False, verbose_name='Dysgraphia'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='dyslexia',
            field=models.BooleanField(default=False, verbose_name='Dyslexia'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='emotional_distubance',
            field=models.BooleanField(default=False, verbose_name='Emotional Disturbance'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='hard_of_hearing',
            field=models.BooleanField(default=False, verbose_name='Hard of Hearing'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='intellectual_disability',
            field=models.BooleanField(default=False, verbose_name='Intellectual Disability'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='k12_iep',
            field=models.BooleanField(default=False, verbose_name='Had an IEP in K-12'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='learning_disability',
            field=models.BooleanField(default=False, verbose_name='Specific Learning Disability'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='multiple_disabilities',
            field=models.BooleanField(default=False, verbose_name='Multiple Disabilities'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='neurological_impairments',
            field=models.BooleanField(default=False, verbose_name='Related to Neurological Impairments'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='orthopedic_impairment',
            field=models.BooleanField(default=False, verbose_name='Orthopedic Impairment'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='other_health_impairment',
            field=models.BooleanField(default=False, verbose_name='Other Health Impairment'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='speech_or_lang_impairment',
            field=models.BooleanField(default=False, verbose_name='Speech or Language Impairment'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='traumatic_brain_injury',
            field=models.BooleanField(default=False, verbose_name='Traumatic Brain Injury'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='visual_impairment',
            field=models.BooleanField(default=False, verbose_name='Visual Impairment'),
        ),
    ]
