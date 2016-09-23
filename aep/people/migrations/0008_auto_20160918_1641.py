# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-18 21:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.datetime_safe


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0007_auto_20160918_1409'),
    ]

    operations = [
        migrations.RunSQL(
            'SET CONSTRAINTS ALL IMMEDIATE',
            reverse_sql=migrations.RunSQL.noop
        ),
        migrations.CreateModel(
            name='WIOA',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='staff',
            name='ec_relation',
            field=models.CharField(choices=[('F', 'Father'), ('M', 'Mother'), ('S', 'Spouse'), ('B', 'Sibling'), ('F', 'Friend'), ('G', 'Legal Guardian'), ('O', 'Other')], default='O', max_length=1, verbose_name='Relationship'),
        ),
        migrations.AddField(
            model_name='staff',
            name='zip_code',
            field=models.CharField(blank=True, max_length=10, verbose_name='Zip Code'),
        ),
        migrations.AddField(
            model_name='student',
            name='amer_indian',
            field=models.BooleanField(default=False, verbose_name='American Indian or Alaska Native'),
        ),
        migrations.AddField(
            model_name='student',
            name='asian',
            field=models.BooleanField(default=False, verbose_name='Asian'),
        ),
        migrations.AddField(
            model_name='student',
            name='black',
            field=models.BooleanField(default=False, verbose_name='Black or African American'),
        ),
        migrations.AddField(
            model_name='student',
            name='ec_relation',
            field=models.CharField(choices=[('F', 'Father'), ('M', 'Mother'), ('S', 'Spouse'), ('B', 'Sibling'), ('F', 'Friend'), ('G', 'Legal Guardian'), ('O', 'Other')], default='O', max_length=1, verbose_name='Relationship'),
        ),
        migrations.AddField(
            model_name='student',
            name='hispanic_latino',
            field=models.BooleanField(default=False, verbose_name='Hispanic/Latino'),
        ),
        migrations.AddField(
            model_name='student',
            name='other_ID',
            field=models.CharField(blank=True, max_length=20, verbose_name='Other ID, Passport #, Visa info, etc.'),
        ),
        migrations.AddField(
            model_name='student',
            name='pacific_islander',
            field=models.BooleanField(default=False, verbose_name='Native Hawaiian or Pacific Islander'),
        ),
        migrations.AddField(
            model_name='student',
            name='parish',
            field=models.CharField(choices=[('1', 'Outside LA'), ('2', 'Acadia'), ('3', 'Allen'), ('4', 'Ascension'), ('5', 'Assumption'), ('6', 'Avoyelles'), ('7', 'Beauregard'), ('8', 'Bienville'), ('9', 'Bossier'), ('10', 'Caddo'), ('11', 'Calcasieu'), ('12', 'Caldwell'), ('13', 'Cameron'), ('14', 'Catahoula'), ('15', 'Claiborne'), ('16', 'Concordia'), ('17', 'De Soto'), ('18', 'East Baton Rouge'), ('19', 'East Carroll'), ('20', 'East Feliciana'), ('21', 'Evangeline'), ('22', 'Franklin'), ('23', 'Grant'), ('24', 'Iberia'), ('25', 'Iberville'), ('26', 'Jackson'), ('27', 'Jefferson'), ('28', 'Jefferson Davis'), ('29', 'Lafayette'), ('30', 'Lafourche'), ('31', 'La Salle'), ('32', 'Lincoln'), ('33', 'Livingston'), ('34', 'Madison'), ('35', 'Morehouse'), ('36', 'Natchitoches'), ('37', 'Orleans'), ('38', 'Ouachita'), ('39', 'Plaquemines'), ('40', 'Pointe Coupee'), ('41', 'Rapides'), ('42', 'Red River'), ('43', 'Richland'), ('44', 'Sabine'), ('45', 'St. Bernard'), ('46', 'St. Charles'), ('47', 'St. Helena'), ('48', 'St. James'), ('49', 'St. John the Baptist'), ('50', 'St. Landry'), ('51', 'St. Martin'), ('52', 'St. Mary'), ('53', 'St. Tammany'), ('54', 'Tangipahoa'), ('55', 'Tensas'), ('56', 'Terrebonne'), ('57', 'Union'), ('58', 'Vermilion'), ('59', 'Vernon'), ('60', 'Washington'), ('61', 'Webster'), ('62', 'West Baton Rouge'), ('63', 'West Carroll'), ('64', 'West Feliciana'), ('65', 'Winn')], default='37', max_length=2),
        ),
        migrations.AddField(
            model_name='student',
            name='prior_registration',
            field=models.BooleanField(default=False, verbose_name='Have you registered for this program before?'),
        ),
        migrations.AddField(
            model_name='student',
            name='program',
            field=models.CharField(choices=[('C', 'College and Career Readiness - HiSET Prep Classes'), ('E', 'Beginning English Language Classes'), ('D', 'Online Classes'), ('A', 'ACE Program')], default='C', max_length=1),
        ),
        migrations.AddField(
            model_name='student',
            name='white',
            field=models.BooleanField(default=False, verbose_name='White'),
        ),
        migrations.AddField(
            model_name='student',
            name='zip_code',
            field=models.CharField(blank=True, max_length=10, verbose_name='Zip Code'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='alt_phone',
            field=models.CharField(blank=True, max_length=20, verbose_name='Alternate Phone Number'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='dob',
            field=models.DateField(default=django.utils.datetime_safe.date.today, verbose_name='Date of Birth'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='staff',
            name='ec_email',
            field=models.EmailField(blank=True, max_length=40, verbose_name='Email Address'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='ec_phone',
            field=models.CharField(blank=True, max_length=20, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='emergency_contact',
            field=models.CharField(blank=True, max_length=60, verbose_name='Emergency Contact'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='phone',
            field=models.CharField(blank=True, max_length=20, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='state',
            field=models.CharField(blank=True, choices=[('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DC', 'District of Columbia'), ('DE', 'Delaware'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MA', 'Massachusetts'), ('MD', 'Maryland'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VA', 'Virginia'), ('VT', 'Vermont'), ('WV', 'West Virginia'), ('WA', 'Washington'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')], default='LA', max_length=2),
        ),
        migrations.AlterField(
            model_name='staff',
            name='street_address_1',
            field=models.CharField(blank=True, max_length=60, verbose_name='Street Address 1'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='street_address_2',
            field=models.CharField(blank=True, max_length=60, verbose_name='Street Address 2'),
        ),
        migrations.AlterField(
            model_name='student',
            name='US_citizen',
            field=models.BooleanField(default=False, verbose_name='US Citizen'),
        ),
        migrations.AlterField(
            model_name='student',
            name='alt_phone',
            field=models.CharField(blank=True, max_length=20, verbose_name='Alternate Phone Number'),
        ),
        migrations.AlterField(
            model_name='student',
            name='dob',
            field=models.DateField(default=django.utils.datetime_safe.date.today, verbose_name='Date of Birth'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='student',
            name='ec_email',
            field=models.EmailField(blank=True, max_length=40, verbose_name='Email Address'),
        ),
        migrations.AlterField(
            model_name='student',
            name='ec_phone',
            field=models.CharField(blank=True, max_length=20, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='student',
            name='emergency_contact',
            field=models.CharField(blank=True, max_length=60, verbose_name='Emergency Contact'),
        ),
        migrations.AlterField(
            model_name='student',
            name='marital_status',
            field=models.CharField(choices=[('S', 'Single'), ('M', 'Married'), ('D', 'Divorced'), ('W', 'Widowed'), ('O', 'Other')], default='S', max_length=1, verbose_name='Marital Status'),
        ),
        migrations.AlterField(
            model_name='student',
            name='phone',
            field=models.CharField(blank=True, max_length=20, verbose_name='Phone Number'),
        ),
        migrations.AlterField(
            model_name='student',
            name='state',
            field=models.CharField(blank=True, choices=[('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DC', 'District of Columbia'), ('DE', 'Delaware'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MA', 'Massachusetts'), ('MD', 'Maryland'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VA', 'Virginia'), ('VT', 'Vermont'), ('WV', 'West Virginia'), ('WA', 'Washington'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')], default='LA', max_length=2),
        ),
        migrations.AlterField(
            model_name='student',
            name='street_address_1',
            field=models.CharField(blank=True, max_length=60, verbose_name='Street Address 1'),
        ),
        migrations.AlterField(
            model_name='student',
            name='street_address_2',
            field=models.CharField(blank=True, max_length=60, verbose_name='Street Address 2'),
        ),
        migrations.AlterField(
            model_name='student',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='student', to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AddField(
            model_name='wioa',
            name='student',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='WIOA', to='people.Student'),
        ),
        migrations.RunSQL(
            migrations.RunSQL.noop,
            reverse_sql='SET CONSTRAINTS ALL IMMEDIATE'
        ),
    ]