# Generated by Django 4.0.4 on 2022-07-26 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0037_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='schedule_sent',
            field=models.BooleanField(default=False),
        ),
    ]
