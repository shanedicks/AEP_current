# Generated by Django 4.2.10 on 2024-03-04 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0044_section_closed'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='reported',
            field=models.BooleanField(default=False),
        ),
    ]
