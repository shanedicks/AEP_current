# Generated by Django 2.0.7 on 2019-01-27 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0042_auto_20181006_2006'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='notes',
            field=models.TextField(blank=True),
        ),
    ]
