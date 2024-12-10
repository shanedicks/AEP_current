# Generated by Django 5.1.2 on 2024-12-10 19:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coaching', '0001_initial'),
        ('people', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceProvider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('CAREER', 'Career Counseling and Job Placement'), ('EDUCATION', 'GED/HiSET Prep Classes and Testing'), ('WORKFORCE', 'Workforce Development Programs'), ('ACADEMIC', 'Tutoring and Academic Support'), ('MENTAL_HEALTH', 'Mental Health Services'), ('FINANCIAL', 'Financial Assistance'), ('COLLEGE', 'College and Technical School Programs'), ('FAMILY', 'Family and Childcare Support Services'), ('FOOD', 'Food and Nutrition Assistance'), ('HOUSING', 'Housing Assistance'), ('HEALTHCARE', 'Healthcare Services'), ('DIGITAL', 'Digital Literacy Training'), ('LEGAL', 'Legal Aid and Advocacy'), ('MENTORSHIP', 'Youth Mentorship'), ('TRANSPORT', 'Transportation Assistance'), ('LGBTQ', 'LGBTQ+ Support'), ('RECOVERY', 'Substance Abuse Recovery'), ('VOLUNTEER', 'Volunteer Opportunities'), ('VETERANS', 'Veterans Services')], max_length=20)),
                ('phone', models.CharField(max_length=20)),
                ('address', models.CharField(blank=True, max_length=200)),
                ('description', models.TextField()),
                ('eligibility', models.TextField()),
            ],
            options={
                'ordering': ['category', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Accommodations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reads_aloud', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Reading out loud on own')),
                ('reads_with_someone', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Reading together with someone')),
                ('needs_reader', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Being read to by someone')),
                ('uses_text_to_speech', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Text-to-speech software')),
                ('uses_colored_overlays', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Use of colored overlays')),
                ('needs_colored_paper', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Use of colored paper for handouts/printer materials')),
                ('uses_visual_guides', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Visual guides (graphic organizers, story maps)')),
                ('takes_reading_notes', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Note taking while reading')),
                ('uses_text_marking', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Highlighting, underlining, text marking')),
                ('reading_other', models.CharField(blank=True, max_length=255, verbose_name='Other reading accommodations')),
                ('oral_before_writing', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Telling the story out loud before writing it')),
                ('uses_word_prediction', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Use of word prediction')),
                ('uses_dictation', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Use of text to speech and dictation software/features')),
                ('uses_spell_check', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Use of spell checkers')),
                ('needs_multiple_revisions', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Revising and editing multiple times')),
                ('writing_other', models.CharField(blank=True, max_length=255, verbose_name='Other writing accommodations')),
                ('needs_demonstration', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Instructor shows me how something is done')),
                ('needs_explanation', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Instructor tells me how I could understand')),
                ('records_lectures', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Recording lectures to listen multiple times')),
                ('uses_teacher_videos', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Viewing recorded videos by the teacher')),
                ('needs_glossaries', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Use of short glossaries for common terms')),
                ('needs_captions', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Use of closed captioning in videos')),
                ('uses_visual_aids', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Use of visual guides: graphic organizers and story maps')),
                ('uses_pictures', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Seeing or drawing pictures of what I am learning')),
                ('needs_clear_expectations', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Knowing what I am expected to learn')),
                ('works_in_pairs', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Working in pairs')),
                ('needs_cultural_context', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Knowing the cultural context')),
                ('asks_questions', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Asking questions')),
                ('uses_sentence_pausing', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Pausing/rephrasing each sentence')),
                ('uses_paragraph_pausing', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Pausing and retelling/rewriting each paragraph')),
                ('makes_lists', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Making lists on my own')),
                ('makes_glossaries', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Making my own glossaries')),
                ('comprehension_other', models.CharField(blank=True, max_length=255, verbose_name='Other comprehension accommodations')),
                ('uses_math_visuals', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Use of visual organizers')),
                ('uses_manipulatives', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Use of manipulatives')),
                ('uses_math_software', models.CharField(choices=[('used', 'Used Successfully in the Past'), ('willing', 'Willing to try'), ('not_interested', 'Not Interested')], max_length=15, verbose_name='Use of math/logic/simulation software')),
                ('math_other', models.CharField(blank=True, max_length=255, verbose_name='Other math accommodations')),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='accommodations', to='people.student')),
            ],
        ),
        migrations.CreateModel(
            name='PerformanceDomainScreening',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seeing_difficulty', models.CharField(choices=[('0', 'No difficulty'), ('1', 'Mild difficulty'), ('2', 'Moderate difficulty'), ('3', 'Severe difficulty'), ('4', 'Cannot do')], verbose_name='How difficult is it to see text/white board?')),
                ('hearing_difficulty', models.CharField(choices=[('0', 'No difficulty'), ('1', 'Mild difficulty'), ('2', 'Moderate difficulty'), ('3', 'Severe difficulty'), ('4', 'Cannot do')], verbose_name='How difficult is it to see your teacher/classmates?')),
                ('reading_difficulty', models.CharField(choices=[('0', 'No difficulty'), ('1', 'Mild difficulty'), ('2', 'Moderate difficulty'), ('3', 'Severe difficulty'), ('4', 'Cannot do')], verbose_name='How difficult is it for you to read?')),
                ('writing_difficulty', models.CharField(choices=[('0', 'No difficulty'), ('1', 'Mild difficulty'), ('2', 'Moderate difficulty'), ('3', 'Severe difficulty'), ('4', 'Cannot do')], verbose_name='How difficult is it for you to write?')),
                ('math_difficulty', models.CharField(choices=[('0', 'No difficulty'), ('1', 'Mild difficulty'), ('2', 'Moderate difficulty'), ('3', 'Severe difficulty'), ('4', 'Cannot do')], verbose_name='How difficult is math?')),
                ('problem_solving_difficulty', models.CharField(choices=[('0', 'No difficulty'), ('1', 'Mild difficulty'), ('2', 'Moderate difficulty'), ('3', 'Severe difficulty'), ('4', 'Cannot do')], verbose_name='How difficult is it to figure out steps to solve a problem?')),
                ('speaking_difficulty', models.CharField(choices=[('0', 'No difficulty'), ('1', 'Mild difficulty'), ('2', 'Moderate difficulty'), ('3', 'Severe difficulty'), ('4', 'Cannot do')], verbose_name='How difficult is it to speak to your teacher/classmates/neighbors/others?')),
                ('lifting_difficulty', models.CharField(choices=[('0', 'No difficulty'), ('1', 'Mild difficulty'), ('2', 'Moderate difficulty'), ('3', 'Severe difficulty'), ('4', 'Cannot do')], verbose_name='How difficult is it to lift things? Are you in pain when lifting?')),
                ('walking_difficulty', models.CharField(choices=[('0', 'No difficulty'), ('1', 'Mild difficulty'), ('2', 'Moderate difficulty'), ('3', 'Severe difficulty'), ('4', 'Cannot do')], verbose_name='How difficult is it for you to walk? Are you in pain when walking?')),
                ('stress_management', models.CharField(choices=[('0', 'No difficulty'), ('1', 'Mild difficulty'), ('2', 'Moderate difficulty'), ('3', 'Severe difficulty'), ('4', 'Cannot do')], verbose_name='How difficult is it for you to manage stress?')),
                ('sleep_difficulty', models.CharField(choices=[('0', 'No difficulty'), ('1', 'Mild difficulty'), ('2', 'Moderate difficulty'), ('3', 'Severe difficulty'), ('4', 'Cannot do')], verbose_name='How difficult is it to get enough sleep?')),
                ('community_access', models.CharField(choices=[('0', 'No difficulty'), ('1', 'Mild difficulty'), ('2', 'Moderate difficulty'), ('3', 'Severe difficulty'), ('4', 'Cannot do')], verbose_name='How difficult is to for you to get around and be social?')),
                ('learning_environment', models.CharField(choices=[('quiet', 'Quiet space (ear mufflers, white noise, etc.)'), ('noise', 'Noise (e.g., listening to music while learning)'), ('extra_time', 'Extra time on task'), ('other', 'Other')], max_length=20, verbose_name='What surroundings help you learn?')),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pd_screening', to='people.student')),
            ],
        ),
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_referred', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('CONTACTED', 'Provider Contacted'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('UNSUCCESSFUL', 'Unsuccessful')], default='PENDING', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('followup_date', models.DateField(blank=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('staff_member', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='referrals_made', to='people.staff')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_referrals', to='people.student')),
                ('service_provider', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='client_referrals', to='coaching.serviceprovider')),
            ],
            options={
                'ordering': ['-date_referred'],
            },
        ),
    ]
