# Generated by Django 2.0.7 on 2019-01-04 20:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('coaching', '0020_auto_20190104_1942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meetingnote',
            name='meeting_date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='meetingnote',
            name='meeting_topic',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='meetingnote',
            name='next_steps',
            field=models.TextField(blank=True),
        ),
    ]