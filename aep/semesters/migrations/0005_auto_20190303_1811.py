# Generated by Django 2.0.7 on 2019-03-03 18:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('semesters', '0004_semester_allowed_absences'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='semester',
            options={'ordering': ['-end_date']},
        ),
    ]
