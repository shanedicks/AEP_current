# Generated by Django 2.0.7 on 2019-04-27 22:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0024_site'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='site_link',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='sections', to='sections.Site'),
        ),
    ]
