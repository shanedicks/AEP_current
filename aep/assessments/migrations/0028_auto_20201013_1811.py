# Generated by Django 3.0.8 on 2020-10-13 18:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0027_auto_20201012_2054'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testhistory',
            name='efl',
        ),
        migrations.RemoveField(
            model_name='testhistory',
            name='tracking_subject',
        ),
    ]
