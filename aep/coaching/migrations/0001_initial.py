# Generated by Django 5.1.2 on 2024-10-29 18:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('people', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AceRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ace_status', models.CharField(blank=True, choices=[('Applicant', 'Applicant'), ('Pending', 'Pending'), ('Deferred', 'Deferred'), ('Active', 'Active'), ('InActive', 'InActive'), ('Completed', 'Completed')], max_length=9)),
                ('status_updated', models.DateField(blank=True, null=True)),
                ('intake_semester', models.CharField(blank=True, choices=[('Fall', 'Fall'), ('Spring', 'Spring'), ('Summer', 'Summer')], max_length=6)),
                ('intake_year', models.CharField(blank=True, max_length=4)),
                ('lola', models.CharField(blank=True, max_length=9)),
                ('dcc_email', models.EmailField(blank=True, max_length=40)),
                ('ace_pathway', models.CharField(blank=True, choices=[('Healthcare', 'Healthcare'), ('Skilled Crafts', 'Skilled Crafts'), ('IT', 'IT'), ('Hospitality', 'Culinary Arts / Hospitality')], max_length=15)),
                ('program', models.CharField(blank=True, max_length=40)),
                ('hsd', models.CharField(blank=True, choices=[('HSE', 'HSE'), ('HSD', 'HSD'), ('Neither', 'Neither')], default='Neither', max_length=7, verbose_name='Diploma')),
                ('hsd_date', models.DateField(blank=True, null=True, verbose_name='Diploma Date')),
                ('media_release', models.BooleanField(default=False)),
                ('third_party_release', models.BooleanField(default=False)),
                ('read_072', models.BooleanField(default=False, verbose_name='Passed Townsend')),
                ('eng_062', models.BooleanField(default=False, verbose_name='Passed ENG 062')),
                ('math_092', models.BooleanField(default=False, verbose_name='Passed MATH 092')),
                ('math_098', models.BooleanField(default=False, verbose_name='Passed MATH 098')),
                ('five_for_six', models.BooleanField(default=False, verbose_name='5 for 6 Scholarship')),
                ('five_for_six_year', models.CharField(blank=True, max_length=4)),
                ('five_for_six_semester', models.CharField(blank=True, choices=[('Fall', 'Fall'), ('Spring', 'Spring'), ('Summer', 'Summer')], max_length=6)),
                ('reading_exit', models.BooleanField(default=False, verbose_name='Passed Reading Exit Exam')),
                ('writing_exit', models.BooleanField(default=False, verbose_name='Passed Writing Exit Exam')),
                ('math_exit', models.BooleanField(default=False, verbose_name='Passed Math Exit Exam')),
                ('nccer_cert', models.BooleanField(default=False, verbose_name='NCCER Cert')),
                ('bls_cert', models.BooleanField(default=False, verbose_name='Basic Life Support Cert')),
                ('servsafe_cert', models.BooleanField(default=False, verbose_name='ServSafe Cert')),
                ('microsoft_cert', models.BooleanField(default=False, verbose_name='Microsoft Cert')),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ace_record', to='people.student')),
            ],
        ),
        migrations.CreateModel(
            name='Coaching',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coaching_type', models.CharField(choices=[('elearn', 'eLearn'), ('ace', 'ACE'), ('open', 'Open Coaching')], default='open', help_text='Type of coaching (Choose One)', max_length=6)),
                ('active', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('Active', 'Active'), ('On Hold', 'On Hold'), ('Inactive', 'Inactive'), ('ELL > CCR', 'ELL > CCR'), ('Completed HiSET', 'Completed HiSET')], default='Active', max_length=20)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('coach', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='coachees', to='people.staff')),
                ('coachee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coaches', to='people.student')),
            ],
        ),
        migrations.CreateModel(
            name='ElearnRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('elearn_status', models.CharField(blank=True, choices=[('New', 'New'), ('Applicant', 'Applicant'), ('Pending', 'Pending'), ('On Hold', 'On Hold'), ('Active', 'Active'), ('InActive', 'InActive'), ('Alumni', 'Alumni'), ('Partner', 'Partner'), ('Partner Alumnus', 'Partner Alumnus'), ('Campus', 'Campus')], default='Applicant', max_length=15)),
                ('status_updated', models.DateField(blank=True, null=True)),
                ('intake_date', models.DateField(blank=True, null=True)),
                ('g_suite_email', models.EmailField(blank=True, max_length=60)),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='elearn_record', to='people.student')),
            ],
        ),
        migrations.CreateModel(
            name='MeetingNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meeting_type', models.CharField(choices=[('eLearn', 'eLearn'), ('ACE', 'ACE'), ('Open Coaching', 'Open Coaching')], help_text='Type of coaching (Choose One)', max_length=17)),
                ('contact_type', models.CharField(blank=True, choices=[('email', 'Email'), ('phone', 'Phone'), ('text', 'Text'), ('hangouts', 'Google Hangouts'), ('messenger', 'Facebook Messenger'), ('In person', 'In Person')], max_length=10)),
                ('next_steps', models.TextField(blank=True)),
                ('meeting_topic', models.TextField(blank=True)),
                ('meeting_date', models.DateField()),
                ('student_no_show', models.BooleanField(default=False, help_text='Check this box if the student failed to attend the meeting')),
                ('student_reschedule', models.BooleanField(default=False, help_text='Check this box if the student requested to reschedule the meeting')),
                ('student_cancel', models.BooleanField(default=False, help_text='Check this box if the student cancelled the meeting')),
                ('coach_cancel', models.BooleanField(default=False, help_text='Check this box if the coach cancelled the meeting')),
                ('low_grades', models.BooleanField(default=False, verbose_name='Concern: Low Grades')),
                ('class_absences', models.BooleanField(default=False, verbose_name='Concern: Class Absences')),
                ('meeting_absences', models.BooleanField(default=False, verbose_name='Concern: Meeting Absences')),
                ('cannot_reach', models.BooleanField(default=False, verbose_name='Concern: Coach Unable to Reach')),
                ('ace_withdrawl', models.BooleanField(default=False, verbose_name='Withdawing from Ace')),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('duration', models.TextField(blank=True, choices=[('15', '15 min'), ('30', '30 min'), ('45', '45 min'), ('60', '60 min')], max_length=3)),
                ('multiple_days', models.BooleanField(default=False, verbose_name='Meeting took place over multiple days')),
                ('progress', models.TextField(blank=True, help_text='Progress on Next Steps')),
                ('notes', models.TextField(blank=True)),
                ('coaching', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='coaching.coaching')),
            ],
            options={
                'ordering': ['-meeting_date'],
            },
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
                ('device', models.CharField(max_length=50, verbose_name='What device will you be using for online learning?(e.g Phone, Tablet, Computer, etc.)')),
                ('contact_preference', models.CharField(choices=[('Call', 'Call'), ('Text', 'Text'), ('Email', 'Email'), ('Social Media', 'Social Media'), ('Google Chat', 'Google Chat')], max_length=12, verbose_name='How do you prefer to be contacted?')),
                ('other_contact', models.CharField(blank=True, max_length=40)),
                ('availability', models.CharField(blank=True, choices=[('Morning', 'Morning (8am - 12am)'), ('Afternoon', 'Afternoon (12am - 4pm)'), ('Evening', 'Early Evening (4pm - 8pm)')], max_length=11, verbose_name='What is your typical availability?')),
                ('other_availability', models.CharField(blank=True, max_length=40)),
                ('library', models.CharField(choices=[('Yes Close and Card', 'Yes, I live close and I have a card'), ('Yes Close', 'Yes, I live close'), ('No not Near', "No, I don't live near a library"), ('No Access Hours', "No, I don't have access to a library during the hours they are open."), ('Unsure', "I'm not sure if I live near a library.")], max_length=20, verbose_name='Do you have access to a local library?')),
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
                ('best_classes', models.TextField(verbose_name='What classes were you best at?')),
                ('worst_classes', models.TextField(verbose_name='What classes did you struggle with the most?')),
                ('favorite_subject', models.TextField(help_text='For example:  "Social Studies was my favorite subject, because we often got to debate and discuss what was going on in the world."', verbose_name='What was your favorite subject and why was it your favorite subject?')),
                ('completion_time', models.CharField(help_text='Note: we use this information to help create a custom academic path for you - the quicker you want to complete, the more work we will advise you to take on.', max_length=140, verbose_name='How quickly do you want to complete the program? (e.g. within one month, within a few months, by end of year)')),
                ('hours_per_week', models.CharField(max_length=140, verbose_name='How much time per week can you dedicate to the program? (use # of hours)')),
                ('personal_goal', models.TextField(verbose_name='What is a personal goal you have for yourself this year? How about five years from now?')),
                ('frustrated', models.TextField(verbose_name='When you get stressed or frustrated, how can I best support you as a coach?')),
                ('anything_else', models.TextField(verbose_name='Is there anything else you want to tell me?')),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='coaching_profile', to='people.student')),
            ],
            options={
                'ordering': ['student__last_name', 'student__first_name'],
            },
        ),
    ]
