# Generated by Django 2.0.7 on 2019-09-09 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0030_auto_20190906_1916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='att_hours',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
