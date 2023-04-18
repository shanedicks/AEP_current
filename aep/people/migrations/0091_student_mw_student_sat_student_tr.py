# Generated by Django 4.1.6 on 2023-04-11 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0090_alter_paperwork_technology'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='mw',
            field=models.BooleanField(default=False, verbose_name='Monday and Wednesday'),
        ),
        migrations.AddField(
            model_name='student',
            name='sat',
            field=models.BooleanField(default=False, verbose_name='Saturday'),
        ),
        migrations.AddField(
            model_name='student',
            name='tr',
            field=models.BooleanField(default=False, verbose_name='Tuesday and Thursday'),
        ),
    ]