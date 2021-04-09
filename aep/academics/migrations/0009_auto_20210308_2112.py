# Generated by Django 3.0.8 on 2021-03-08 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0063_auto_20210205_1713'),
        ('academics', '0008_skillmastery_mastered'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coursecompletion',
            options={'verbose_name_plural': 'Course Completions'},
        ),
        migrations.AlterModelOptions(
            name='skill',
            options={'ordering': ['title']},
        ),
        migrations.AlterModelOptions(
            name='skillmastery',
            options={'ordering': ['skill'], 'verbose_name_plural': 'Skill Masteries'},
        ),
        migrations.AddField(
            model_name='course',
            name='skills_view',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterUniqueTogether(
            name='certificate',
            unique_together={('student', 'credential')},
        ),
        migrations.AlterUniqueTogether(
            name='coursecompletion',
            unique_together={('student', 'course')},
        ),
        migrations.AlterUniqueTogether(
            name='skillmastery',
            unique_together={('student', 'skill')},
        ),
    ]