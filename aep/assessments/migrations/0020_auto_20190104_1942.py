# Generated by Django 2.0.7 on 2019-01-04 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0019_auto_20180712_0140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tabe',
            name='form',
            field=models.CharField(choices=[('9', '9'), ('10', '10'), ('11', '11'), ('12', '12')], max_length=2),
        ),
    ]
