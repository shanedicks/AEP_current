# Generated by Django 4.0.4 on 2022-12-09 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0089_paperwork_pic_id_file_alter_paperwork_g_sig_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paperwork',
            name='technology',
            field=models.BooleanField(default=False, verbose_name='Technology Usage Agreement'),
        ),
    ]
