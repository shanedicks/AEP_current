# Generated by Django 2.0.7 on 2019-06-26 20:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0026_transfer_sites'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='section',
            name='site',
        ),
    ]
