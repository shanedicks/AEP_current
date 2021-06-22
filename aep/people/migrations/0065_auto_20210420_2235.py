# Generated by Django 3.0.8 on 2021-04-20 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0064_auto_20210402_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wioa',
            name='highet_level_at_entry',
            field=models.CharField(choices=[('0', 'NO SCHOOL GRADE COMPLETED'), ('1', 'COMPLETED 1 YEAR'), ('2', 'COMPLETED 2 YEARS'), ('3', 'COMPLETED 3 YEARS'), ('4', 'COMPLETED 4 YEARS'), ('5', 'COMPLETED 5 YEARS'), ('6', 'COMPLETED 6 YEARS'), ('7', 'COMPLETED 7 YEARS'), ('8', 'COMPLETED 8 YEARS'), ('9', 'COMPLETED 9 YEARS'), ('10', 'COMPLETED 10 YEARS'), ('11', 'COMPLETED 11 YEARS'), ('12', 'COMPLETED 12 YEARS')], default='1', max_length=2),
        ),
    ]