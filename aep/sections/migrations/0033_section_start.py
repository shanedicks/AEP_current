# Generated by Django 3.0.8 on 2020-08-13 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0032_auto_20200409_2007'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='start',
            field=models.DateField(blank=True, null=True),
        ),
    ]