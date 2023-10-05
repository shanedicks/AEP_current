# Generated by Django 4.2.4 on 2023-10-05 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0041_cancellation_send_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='status',
            field=models.CharField(choices=[('A', 'Active'), ('W', 'Waitlist'), ('R', 'Withdrawn'), ('D', 'Dropped'), ('C', 'Completed'), ('T', 'Needs Test')], default='A', max_length=1),
        ),
    ]
