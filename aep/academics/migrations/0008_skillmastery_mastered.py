# Generated by Django 3.0.8 on 2021-02-26 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0007_auto_20210204_2013'),
    ]

    operations = [
        migrations.AddField(
            model_name='skillmastery',
            name='mastered',
            field=models.BooleanField(default=False),
        ),
    ]
