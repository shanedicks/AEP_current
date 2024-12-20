# Generated by Django 5.1.2 on 2024-12-10 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestingAccommodations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dcccaep_approved', models.CharField(choices=[('yes', 'Yes'), ('no', 'No'), ('review', 'Needs Further Review')], max_length=10, verbose_name='Is the student approved by DCCCAEP for Accommodations')),
                ('private_room', models.BooleanField(verbose_name='Private Room')),
                ('text_to_speech', models.BooleanField(verbose_name='Text to Speech')),
                ('testing_time', models.CharField(choices=[('1.25', '1.25x Time'), ('1.5', '1.5x Time'), ('2', '2x Time'), ('untimed', 'Untimed')], max_length=10, verbose_name='Testing Time')),
                ('preferred_accommodation', models.TextField(verbose_name='Preferred Accommodation')),
                ('environmental_facilitator', models.TextField(verbose_name='Environmental Facilitator')),
                ('start_date', models.DateField(verbose_name='Start Date')),
                ('review_date', models.DateField(verbose_name='Review Date')),
            ],
        ),
    ]
