# Generated by Django 3.0.8 on 2021-01-21 22:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0062_auto_20201019_2302'),
        ('academics', '0004_auto_20190605_2211'),
    ]

    operations = [
        migrations.CreateModel(
            name='Credential',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CourseCompletion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cert_date', models.DateField()),
                ('certifier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='coursecompletion_issued', to='people.Staff')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='students', to='academics.Course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='coursecompletions_earned', to='people.Student')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cert_date', models.DateField()),
                ('certifier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='certificate_issued', to='people.Staff')),
                ('credential', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='students', to='academics.Credential')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='certificates_earned', to='people.Student')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]