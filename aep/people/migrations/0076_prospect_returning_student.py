# Generated by Django 3.0.14 on 2021-12-01 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0075_auto_20211109_2141'),
    ]

    operations = [
        migrations.AddField(
            model_name='prospect',
            name='returning_student',
            field=models.BooleanField(default=False, verbose_name='Probable Returning Student'),
        ),
    ]
