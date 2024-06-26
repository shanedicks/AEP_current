# Generated by Django 4.2.10 on 2024-04-04 22:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assessments', '0044_testhistory_hiset_authorization_form'),
    ]

    operations = [
        migrations.AddField(
            model_name='testappointment',
            name='creator',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='created_appointments', to=settings.AUTH_USER_MODEL),
        ),
    ]
