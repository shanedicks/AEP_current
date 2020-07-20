# Generated by Django 2.2.10 on 2020-04-09 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0025_auto_20191211_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testappointment',
            name='attendance_type',
            field=models.CharField(choices=[('P', 'Present'), ('A', 'Absent'), ('X', '-----')], default='X', max_length=1),
        ),
    ]