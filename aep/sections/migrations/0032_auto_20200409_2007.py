# Generated by Django 2.2.10 on 2020-04-09 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0031_auto_20190909_1919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='attendance_type',
            field=models.CharField(choices=[('P', 'Present'), ('A', 'Absent'), ('X', '-----'), ('C', 'Cancelled')], default='X', max_length=1),
        ),
    ]
