# Generated by Django 3.0.8 on 2020-08-28 20:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0055_auto_20200813_2006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='intake_date',
            field=models.DateField(blank=True, default=datetime.date(2020, 8, 28), null=True),
        ),
    ]