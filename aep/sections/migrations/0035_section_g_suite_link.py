# Generated by Django 3.0.14 on 2021-08-19 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0034_auto_20200813_2039'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='g_suite_link',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]