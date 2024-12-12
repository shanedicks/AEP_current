# Generated by Django 5.1.2 on 2024-12-10 19:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0002_testingaccommodations'),
    ]

    operations = [
        migrations.AddField(
            model_name='testingaccommodations',
            name='student',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='accomodations', to='assessments.testhistory'),
            preserve_default=False,
        ),
    ]