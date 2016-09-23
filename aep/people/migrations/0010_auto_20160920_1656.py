# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-20 16:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0009_auto_20160918_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='country',
            field=models.CharField(blank=True, max_length=20, verbose_name='Country of Highest Education'),
        ),
        migrations.AddField(
            model_name='student',
            name='native_language',
            field=models.CharField(blank=True, max_length=20, verbose_name='Native Language'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='adult_one_stop',
            field=models.CharField(choices=[('1', 'Yes, Local Formula'), ('2', 'Yes, Statewide'), ('3', 'Yes, Both Local and Statewide'), ('4', 'No')], default='4', max_length=1),
        ),
        migrations.AddField(
            model_name='wioa',
            name='aged_out_foster_care',
            field=models.BooleanField(default=False, verbose_name='Aged out of Foster Care'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='arrest_record_employment_barrier',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='cult_barriers_hind_emp',
            field=models.BooleanField(default=False, verbose_name='Cultural Barriers Hindering Employment'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='current_employment_status',
            field=models.CharField(choices=[('1', 'Employed'), ('2', 'Unemployed'), ('3', 'Unemployed - Not looking for work'), ('4', 'Not in labor force'), ('5', 'Employed, but recieved notice of termination or Military seperation is pending'), ('6', 'Not in labor force and/or not looking for work')], default='2', max_length=2, verbose_name='Current Employment Status'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='disability_1',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='disability_10',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='disability_11',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='disability_12',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='disability_13',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='disability_14',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='disability_15',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='disability_2',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='disability_3',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='disability_4',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='disability_5',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='disability_6',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='disability_7',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='disability_8',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='disability_9',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='disability_status',
            field=models.CharField(blank=True, choices=[('1', 'Yes'), ('2', 'No'), ('3', 'Unknown')], max_length=1),
        ),
        migrations.AddField(
            model_name='wioa',
            name='disabled_in_poverty',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='dislearning_1',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='dislearning_2',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='dislearning_3',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='dislearning_4',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='dislocated_worker',
            field=models.BooleanField(default=False, verbose_name='Dislocated Worker'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='displaced_homemaker',
            field=models.BooleanField(default=False, verbose_name='Displaced Homemaker'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='employer',
            field=models.CharField(blank=True, max_length=25, verbose_name='Employer'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='etp_CIP_Code',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='wioa',
            name='etp_name',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='wioa',
            name='etp_program',
            field=models.CharField(blank=True, choices=[('1', 'A program of study leading to an industry-recognized certificate or certification'), ('2', 'A program of study leading to a certificate of completion of an apprenticeship'), ('3', 'A program of study leading to a license recognized by the State involved or the Federal Government'), ('4', 'A program of study leading to an associate degree'), ('5', 'A program of study leading to a baccalaureate degree'), ('6', 'A program of study leading to a community college certificate of completion'), ('7', 'A program of study leading to a secondary school diploma or its equivalent'), ('8', 'A program of study leading to employment'), ('9', 'A program of study leading to a measureable skills gain leading to a credentiacredential or employmentment'), ('10', 'Youth Occupational Skills Training')], max_length=2),
        ),
        migrations.AddField(
            model_name='wioa',
            name='exhaust_tanf',
            field=models.BooleanField(default=False, verbose_name='Exhausting TANF Within 2 Years'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='free_lunch_youth',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='highest_level_completed',
            field=models.CharField(choices=[('1', 'NO FORMAL SCHOOL'), ('2', 'COMPLETED 1 YEAR'), ('3', 'COMPLETED 2 YEARS'), ('4', 'COMPLETED 3 YEARS'), ('5', 'COMPLETED 4 YEARS'), ('6', 'COMPLETED 5 YEARS'), ('7', 'COMPLETED 6 YEARS'), ('8', 'COMPLETED 7 YEARS'), ('9', 'COMPLETED 8 YEARS'), ('10', 'COMPLETED 9 YEARS'), ('11', 'COMPLETED 10 YEARS'), ('12', 'COMPLETED 11 YEARS'), ('13', 'COMPLETED 12 YEARS (HS DIPLOMA NOT EARNED)'), ('14', 'COMPLETED 13 YEARS'), ('15', 'COMP 14 YEARS/ASSC DEG/TECHNICAL DIPLOMA'), ('16', 'COMPLETED 15 YEARS'), ('17', 'COMPLETED BACHELOR DEGREE'), ('18', 'COMPLETED BEYOND BACHELOR DEGREE'), ('19', 'HIGH SCHOOL EQUIVALENCY'), ('20', 'CERTIFICATE OF ATTENDANCE OR COMPLETION (HS ONLY)'), ('21', 'POST SECONDARY DEGREE/CERTIFICATE EARNED'), ('22', 'COMPLETED 12 YEARS (HS DIPLOMA EARNED)')], default='1', max_length=2),
        ),
        migrations.AddField(
            model_name='wioa',
            name='highet_level_at_entry',
            field=models.CharField(choices=[('1', 'NO SCHOOL GRADE COMPLETED'), ('2', 'COMPLETED 1 YEAR'), ('3', 'COMPLETED 2 YEARS'), ('4', 'COMPLETED 3 YEARS'), ('5', 'COMPLETED 4 YEARS'), ('6', 'COMPLETED 5 YEARS'), ('7', 'COMPLETED 6 YEARS'), ('8', 'COMPLETED 7 YEARS'), ('9', 'COMPLETED 8 YEARS'), ('10', 'COMPLETED 9 YEARS'), ('11', 'COMPLETED 10 YEARS'), ('12', 'COMPLETED 11 YEARS'), ('13', 'COMPLETED 12 YEARS')], default='1', max_length=2),
        ),
        migrations.AddField(
            model_name='wioa',
            name='homeless',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='in_foster_care',
            field=models.BooleanField(default=False, verbose_name='In Foster Care'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='irregular_sleep_accomodation',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='job_corps',
            field=models.CharField(blank=True, choices=[('1', 'Yes'), ('2', 'No'), ('3', 'Unknown')], max_length=1),
        ),
        migrations.AddField(
            model_name='wioa',
            name='lacks_adequate_residence',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='long_term_unemployed',
            field=models.BooleanField(default=False, help_text='More than 27 consecutive weeks', verbose_name='Long-term Unemployed'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='low_family_income',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='low_income',
            field=models.BooleanField(default=False, verbose_name='Low Income'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='low_literacy',
            field=models.BooleanField(default=False, verbose_name='Low Literacy'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='migrant_seasonal_status',
            field=models.CharField(choices=[('1', 'Seasonal Farmworker'), ('2', 'Migrant and Seasonal Farmworker'), ('3', 'A Dependant of a Seasonal, or Migrant and Seasonal Farmworker'), ('4', 'No')], default='4', max_length=2, verbose_name='Migrant and Seasonal Farmworker Status'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='migratory_child',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='occupation',
            field=models.CharField(blank=True, max_length=25, verbose_name='Employer'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='public_assistance',
            field=models.BooleanField(default=False, verbose_name='Public Assistance'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='recieved_training',
            field=models.CharField(choices=[('1', 'Yes'), ('2', 'No')], default='2', max_length=1),
        ),
        migrations.AddField(
            model_name='wioa',
            name='recieves_public_assistance',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='runaway_youth',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='rural_area',
            field=models.BooleanField(default=False, verbose_name='Rural Area'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='school_location',
            field=models.CharField(choices=[('', 'Please Select'), ('1', 'US Based'), ('2', 'Non-US Based')], default='1', max_length=1),
        ),
        migrations.AddField(
            model_name='wioa',
            name='school_status',
            field=models.CharField(blank=True, choices=[('1', 'In-School, H.S. or less'), ('2', 'In-School, Alternative School'), ('3', 'In-School, Post H.S.'), ('4', 'Not attending school or H.S. dropout'), ('5', 'Not attending school; H.S. graduate'), ('6', 'Not attending school; within age of compulsory school attendance')], max_length=1),
        ),
        migrations.AddField(
            model_name='wioa',
            name='single_parent',
            field=models.BooleanField(default=False, verbose_name='Single Parent'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='state_payed_foster',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='subject_of_criminal_justice',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='training_type_1',
            field=models.CharField(blank=True, choices=[('1', 'On the Job Training'), ('2', 'Skill Upgrading'), ('3', 'Entrepreneurial Training (non-WIOA Youth)'), ('4', 'ABE or ESL in conjunction with Training (non-TAA funded)'), ('5', 'Customized Training'), ('6', 'Other Occupational Skills Training'), ('7', 'Remedial Training (ABE/ESL – TAA only)'), ('8', 'Prerequisite Training'), ('9', 'Registered Apprenticeship'), ('10', 'Youth Occupational Skills Training'), ('11', 'Other Non-Occupational-Skills Training'), ('0', 'No Training Service')], max_length=2),
        ),
        migrations.AddField(
            model_name='wioa',
            name='training_type_2',
            field=models.CharField(blank=True, choices=[('1', 'On the Job Training'), ('2', 'Skill Upgrading'), ('3', 'Entrepreneurial Training (non-WIOA Youth)'), ('4', 'ABE or ESL in conjunction with Training (non-TAA funded)'), ('5', 'Customized Training'), ('6', 'Other Occupational Skills Training'), ('7', 'Remedial Training (ABE/ESL – TAA only)'), ('8', 'Prerequisite Training'), ('9', 'Registered Apprenticeship'), ('10', 'Youth Occupational Skills Training'), ('11', 'Other Non-Occupational-Skills Training'), ('0', 'No Training Service')], max_length=2),
        ),
        migrations.AddField(
            model_name='wioa',
            name='training_type_3',
            field=models.CharField(blank=True, choices=[('1', 'On the Job Training'), ('2', 'Skill Upgrading'), ('3', 'Entrepreneurial Training (non-WIOA Youth)'), ('4', 'ABE or ESL in conjunction with Training (non-TAA funded)'), ('5', 'Customized Training'), ('6', 'Other Occupational Skills Training'), ('7', 'Remedial Training (ABE/ESL – TAA only)'), ('8', 'Prerequisite Training'), ('9', 'Registered Apprenticeship'), ('10', 'Youth Occupational Skills Training'), ('11', 'Other Non-Occupational-Skills Training'), ('0', 'No Training Service')], max_length=2),
        ),
        migrations.AddField(
            model_name='wioa',
            name='voc_rehab',
            field=models.CharField(choices=[('1', 'Vocational Rehabilitation'), ('2', 'Vocational Rehabilitation and Employment, Statewide'), ('3', 'Both, VR and VR&E'), ('4', 'No')], default='4', max_length=1),
        ),
        migrations.AddField(
            model_name='wioa',
            name='wagner_peyser',
            field=models.CharField(choices=[('1', 'Yes'), ('2', 'No'), ('3', 'Unknown')], default='3', max_length=1),
        ),
        migrations.AddField(
            model_name='wioa',
            name='youth_build',
            field=models.CharField(blank=True, choices=[('1', 'Yes'), ('2', 'No'), ('3', 'Unknown')], max_length=1),
        ),
        migrations.AddField(
            model_name='wioa',
            name='youth_in_high_poverty_area',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='wioa',
            name='youth_one_stop',
            field=models.CharField(choices=[('1', 'Yes, Local Formula'), ('2', 'Yes, Statewide'), ('3', 'Yes, Both Local and Statewide'), ('4', 'No')], default='4', max_length=1),
        ),
    ]