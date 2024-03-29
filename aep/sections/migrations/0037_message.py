# Generated by Django 3.0.14 on 2022-01-17 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0036_auto_20211109_2056'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('message', models.CharField(max_length=160)),
                ('sent', models.DateTimeField(blank=True, null=True)),
                ('sections', models.ManyToManyField(to='sections.Section')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
    ]
