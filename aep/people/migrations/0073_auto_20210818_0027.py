# Generated by Django 3.0.14 on 2021-08-18 00:27

from django.db import migrations, models
import people.models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0072_auto_20210818_0016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prospect',
            name='slug',
            field=models.CharField(default=people.models.make_prospect_slug, max_length=5),
        ),
    ]
