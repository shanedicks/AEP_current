# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-18 21:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('people', '0029_auto_20170503_1300'),
    ]

    operations = [
        migrations.CreateModel(
            name='AceRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lola', models.CharField(blank=True, max_length=9)),
                ('dcc_email', models.EmailField(blank=True, max_length=40)),
                ('ace_pathway', models.CharField(choices=[('Healthcare', 'Healthcare'), ('Skilled Crafts', 'Skilled Crafts'), ('IT', 'IT'), ('Hospitality', 'Culinary Arts / Hospitality')], max_length=15)),
                ('program', models.CharField(max_length=1)),
                ('hsd', models.CharField(max_length=1)),
                ('hsd_date', models.DateField()),
                ('media_release', models.BooleanField(default=False)),
                ('third_party_release', models.BooleanField(default=True)),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ace_record', to='people.Student')),
            ],
        ),
        migrations.CreateModel(
            name='Coaching',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('coach', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coachees', to='people.Staff')),
                ('coachee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coaches', to='people.Student')),
            ],
        ),
        migrations.CreateModel(
            name='MeetingNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meeting_type', models.CharField(choices=[('elearn', 'eLearn'), ('ace', 'ACE'), ('open', 'Open Coaching')], help_text='Type of coaching (Choose One)', max_length=6)),
                ('meeting_date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('progress', models.TextField(blank=True, help_text='Progress on Next Steps')),
                ('next_steps', models.TextField(blank=True, help_text='New Next Steps')),
                ('notes', models.TextField(blank=True, help_text='Other Notes')),
                ('coaching', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='coaching.Coaching')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ace_status', models.CharField(choices=[('NA', 'NA'), ('Applicant', 'Applicant'), ('Active', 'Active'), ('InActive', 'InActive'), ('Completed', 'Completed')], default='NA', max_length=10)),
                ('elearn_status', models.CharField(choices=[('NA', 'NA'), ('Applicant', 'Applicant'), ('Active', 'Active'), ('InActive', 'InActive'), ('Completed', 'Completed')], default='NA', max_length=10)),
                ('health_pathway_interest', models.BooleanField(default=False, verbose_name='Healthcare')),
                ('crafts_pathway_interest', models.BooleanField(default=False, verbose_name='Skilled Crafts')),
                ('it_pathway_interest', models.BooleanField(default=False, verbose_name='IT')),
                ('hospitality_pathway_interest', models.BooleanField(default=False, verbose_name='Culinary Arts / Hostpitaliy')),
                ('texts_ok', models.BooleanField(default=False, help_text='Are you okay with elearn sending you text messages?', verbose_name='Text Messages')),
                ('smartphone', models.BooleanField(default=False, help_text='Do you have a smartphone?')),
                ('webcam', models.BooleanField(default=False, help_text='Do you have a webcam with a microphone at home?')),
                ('device', models.CharField(help_text='What device will you be using for online learning?(e.g Phone, Tablet, Computer, etc.)', max_length=50)),
                ('contact_preference', models.CharField(choices=[('Call', 'Call'), ('Text', 'Text'), ('Email', 'Email'), ('Social Media', 'Social Media'), ('Google Chat', 'Google Chat')], help_text='How do you prefer to be contacted?', max_length=1)),
                ('other_contact', models.CharField(blank=True, max_length=40)),
                ('availability', models.CharField(choices=[('Morning', 'Morning'), ('Afternoon', 'Afternoon'), ('Evening', 'Early Evening')], help_text='What is your typical availability?', max_length=11)),
                ('other_availability', models.CharField(blank=True, max_length=40)),
                ('library', models.CharField(choices=[('Yes Close and Card', 'Yes, I live close and I have a card'), ('Yes Close', 'Yes, I live close'), ('No not Near', "No, I don't live near a library"), ('No Access Hours', "No, I don't have access to a library during the hours they are open."), ('Unsure', "I'm not sure if I live near a library.")], max_length=20)),
                ('instagram', models.CharField(blank=True, max_length=40, verbose_name='Optional: Instagram Handle')),
                ('twitter', models.CharField(blank=True, max_length=40, verbose_name='Optional: Twitter Handle')),
                ('facebook', models.CharField(blank=True, max_length=40, verbose_name='Optional: Facebook Handle')),
                ('linkedin', models.CharField(blank=True, max_length=40, verbose_name='Optional: LinkedIn Handle')),
                ('grade_level', models.CharField(choices=[('6', '6th Grade or Lower'), ('7', '7th Grade'), ('8', '8th Grade'), ('9', '9th Grade'), ('10', '10th Grade'), ('11', '11th Grade'), ('O', 'Other')], max_length=2, verbose_name='What was the last grade level you completed?')),
                ('school_experience', models.TextField(help_text='A good start is to tell us your last school attended and a little bit of your story about what brought you to our program! This helps us to get to know and support you in our school!', verbose_name='Tell us about your last school experience')),
                ('special_help', models.CharField(choices=[('Y', 'Yes'), ('N', 'No')], default='N', help_text='Examples of special help: special education services/accommodations, after school or in-school tutoring, counseling services, etc.', max_length=1, verbose_name='Did you ever receive any special help in school OR do you believe you should have? ')),
                ('special_help_desc', models.TextField(blank=True, verbose_name='If you answered yes to the above question, describe below what sort of help you received OR why you believe you should have')),
                ('conditions', models.TextField(blank=True, verbose_name='(OPTIONAL) Do you have any medical conditions you wish to disclose that might impact your academics?')),
                ('elearn_experience', models.CharField(max_length=140, verbose_name='What experience do you have with online learning? (if none, simply put "none" or "NA")')),
                ('math', models.CharField(choices=[('Not', 'Not at all Confident'), ('Some', 'Somewhat Confident'), ('Very', 'Very Confident')], max_length=4)),
                ('english', models.CharField(choices=[('Not', 'Not at all Confident'), ('Some', 'Somewhat Confident'), ('Very', 'Very Confident')], max_length=4)),
                ('social_studies', models.CharField(choices=[('Not', 'Not at all Confident'), ('Some', 'Somewhat Confident'), ('Very', 'Very Confident')], max_length=4)),
                ('science', models.CharField(choices=[('Not', 'Not at all Confident'), ('Some', 'Somewhat Confident'), ('Very', 'Very Confident')], max_length=4)),
                ('best_classes', models.TextField(verbose_name='What classes where you best at?')),
                ('worst_classes', models.TextField(verbose_name='What classes did you struggle with the most?')),
                ('favorite_subject', models.TextField(help_text='For example:  "Social Studies was my favorite subject, because we often got to debate and discuss what was going on in the world."', verbose_name='What was your favorite subject and why was it your favorite subject?')),
                ('completion_time', models.CharField(help_text='Note: we use this information to help create a custom academic path for you - the quicker you want to complete, the more work we will advise you to take on.', max_length=140, verbose_name='How quickly do you want to complete the program? (e.g. within one month, within a few months, by end of year)')),
                ('hours_per_week', models.CharField(max_length=140, verbose_name='How much time per week can you dedicate to the program? (use # of hours)')),
                ('personal_goal', models.TextField(verbose_name='What is a personal goal you have for yourself this year? How about five years from now?')),
                ('frustrated', models.TextField(verbose_name='When you get stressed or frustrated, how can I best support you as a coach?')),
                ('anything_else', models.TextField(verbose_name='Is there anything else you want to tell me?')),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='coaching_profile', to='people.Student')),
            ],
            options={
                'ordering': ['student__user__last_name', 'student__user__first_name'],
            },
        ),
    ]
