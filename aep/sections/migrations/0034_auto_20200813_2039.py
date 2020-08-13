# Generated by Django 3.0.8 on 2020-08-13 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0033_section_start'),
    ]

    operations = [
        migrations.RenameField(
            model_name='section',
            old_name='start',
            new_name='starting',
        ),
        migrations.AddField(
            model_name='section',
            name='ending',
            field=models.DateField(blank=True, null=True),
        ),
    ]
