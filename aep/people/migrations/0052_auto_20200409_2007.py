# Generated by Django 2.2.10 on 2020-04-09 20:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0051_paperwork'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='intake_date',
            field=models.DateField(blank=True, default=datetime.date(2020, 4, 9), null=True),
        ),
    ]
