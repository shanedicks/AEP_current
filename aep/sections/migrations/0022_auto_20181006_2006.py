# Generated by Django 2.0.7 on 2018-10-06 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0021_auto_20180712_0140'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='notes',
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name='attendance',
            name='online',
            field=models.BooleanField(default=False),
        ),
    ]
