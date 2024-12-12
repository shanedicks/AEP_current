# Generated by Django 5.1.2 on 2024-12-10 23:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0004_alter_testingaccommodations_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testingaccommodations',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='accommodations', to='assessments.testhistory'),
        ),
    ]