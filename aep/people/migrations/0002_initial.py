# Generated by Django 5.1.2 on 2024-10-29 18:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('people', '0001_initial'),
        ('sections', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='site_preference',
            field=models.ManyToManyField(blank=True, to='sections.site'),
        ),
        migrations.AddField(
            model_name='student',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='student', to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AddField(
            model_name='prospect',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='prospects', to='people.student'),
        ),
        migrations.AddField(
            model_name='pop',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pop', to='people.student'),
        ),
        migrations.AddField(
            model_name='paperwork',
            name='student',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_paperwork', to='people.student'),
        ),
        migrations.AddField(
            model_name='collegeinterest',
            name='student',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='college_interest', to='people.student'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='student',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='WIOA', to='people.student'),
        ),
        migrations.AlterUniqueTogether(
            name='pop',
            unique_together={('student', 'start_date')},
        ),
    ]
