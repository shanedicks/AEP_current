# Generated by Django 2.2.10 on 2020-04-09 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coaching', '0023_auto_20190911_2000'),
    ]

    operations = [
        migrations.AddField(
            model_name='acerecord',
            name='bls_cert',
            field=models.BooleanField(default=False, verbose_name='Basic Life Support Cert'),
        ),
        migrations.AddField(
            model_name='acerecord',
            name='five_for_six',
            field=models.BooleanField(default=False, verbose_name='5 for 6 Scholarship'),
        ),
        migrations.AddField(
            model_name='acerecord',
            name='five_for_six_semester',
            field=models.CharField(blank=True, choices=[('Fall', 'Fall'), ('Spring', 'Spring'), ('Summer', 'Summer')], max_length=6),
        ),
        migrations.AddField(
            model_name='acerecord',
            name='five_for_six_year',
            field=models.CharField(blank=True, max_length=4),
        ),
        migrations.AddField(
            model_name='acerecord',
            name='math_exit',
            field=models.BooleanField(default=False, verbose_name='Passed Math Exit Exam'),
        ),
        migrations.AddField(
            model_name='acerecord',
            name='microsoft_cert',
            field=models.BooleanField(default=False, verbose_name='Microsoft Cert'),
        ),
        migrations.AddField(
            model_name='acerecord',
            name='nccer_cert',
            field=models.BooleanField(default=False, verbose_name='NCCER Cert'),
        ),
        migrations.AddField(
            model_name='acerecord',
            name='reading_exit',
            field=models.BooleanField(default=False, verbose_name='Passed Reading Exit Exam'),
        ),
        migrations.AddField(
            model_name='acerecord',
            name='servsafe_cert',
            field=models.BooleanField(default=False, verbose_name='ServSafe Cert'),
        ),
        migrations.AddField(
            model_name='acerecord',
            name='writing_exit',
            field=models.BooleanField(default=False, verbose_name='Passed Writing Exit Exam'),
        ),
        migrations.AlterField(
            model_name='acerecord',
            name='hsd',
            field=models.CharField(blank=True, choices=[('HSE', 'HSE'), ('HSD', 'HSD'), ('Neither', 'Neither')], default='Neither', max_length=7, verbose_name='Diploma'),
        ),
        migrations.AlterField(
            model_name='acerecord',
            name='hsd_date',
            field=models.DateField(blank=True, null=True, verbose_name='Diploma Date'),
        ),
    ]
