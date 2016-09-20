from datetime import date
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from core.utils import make_slug, make_AEP_ID


class Profile(models.Model):
    STATE_CHOICES = (
        ("AL", "Alabama"),
        ("AK", "Alaska"),
        ("AZ", "Arizona"),
        ("AR", "Arkansas"),
        ("CA", "California"),
        ("CO", "Colorado"),
        ("CT", "Connecticut"),
        ("DC", "District of Columbia"),
        ("DE", "Delaware"),
        ("FL", "Florida"),
        ("GA", "Georgia"),
        ("HI", "Hawaii"),
        ("ID", "Idaho"),
        ("IL", "Illinois"),
        ("IN", "Indiana"),
        ("IA", "Iowa"),
        ("KS", "Kansas"),
        ("KY", "Kentucky"),
        ("LA", "Louisiana"),
        ("ME", "Maine"),
        ("MA", "Massachusetts"),
        ("MD", "Maryland"),
        ("MI", "Michigan"),
        ("MN", "Minnesota"),
        ("MS", "Mississippi"),
        ("MO", "Missouri"),
        ("MT", "Montana"),
        ("NC", "North Carolina"),
        ("ND", "North Dakota"),
        ("NH", "New Hampshire"),
        ("NJ", "New Jersey"),
        ("NM", "New Mexico"),
        ("NY", "New York"),
        ("NE", "Nebraska"),
        ("NV", "Nevada"),
        ("OH", "Ohio"),
        ("OK", "Oklahoma"),
        ("OR", "Oregon"),
        ("PA", "Pennsylvania"),
        ("RI", "Rhode Island"),
        ("SC", "South Carolina"),
        ("SD", "South Dakota"),
        ("TN", "Tennessee"),
        ("TX", "Texas"),
        ("UT", "Utah"),
        ("VA", "Virginia"),
        ("VT", "Vermont"),
        ("WV", "West Virginia"),
        ("WA", "Washington"),
        ("WI", "Wisconsin"),
        ("WY", "Wyoming")
    )
    EC_RELATIONS_CHOICES = (
        ("F", "Father"),
        ("M", "Mother"),
        ("S", "Spouse"),
        ("B", "Sibling"),
        ("F", "Friend"),
        ("G", "Legal Guardian"),
        ("O", "Other")
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Phone Number"),
    )
    alt_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Alternate Phone Number"),
    )
    street_address_1 = models.CharField(
        max_length=60,
        blank=True,
        verbose_name=_("Street Address 1"),
    )
    street_address_2 = models.CharField(
        max_length=60,
        blank=True,
        verbose_name=("Street Address 2"))
    city = models.CharField(max_length=30, blank=True)
    state = models.CharField(
        max_length=2,
        blank=True,
        choices=STATE_CHOICES,
        default="LA"
    )
    zip_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_("Zip Code")
    )
    dob = models.DateField(
        verbose_name=_("Date of Birth")
    )
    emergency_contact = models.CharField(
        max_length=60,
        blank=True,
        verbose_name=_("Emergency Contact")
    )
    ec_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("EC Phone Number")
    )
    ec_email = models.EmailField(
        max_length=40,
        blank=True,
        verbose_name=_("EC Email Address")
    )
    ec_relation = models.CharField(
        max_length=1,
        choices=EC_RELATIONS_CHOICES,
        default='O',
        blank=True,
        verbose_name=_("EC Relationship")
    )
    # make_slug here creates a 5 character string for use in absolute urls
    slug = models.CharField(
        unique=True,
        default=make_slug,
        max_length=5
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.user.get_full_name()


class Student(Profile):

    PARISH_CHOICES = (
        ("1", "Outside LA"),
        ("2", "Acadia"),
        ("3", "Allen"),
        ("4", "Ascension"),
        ("5", "Assumption"),
        ("6", "Avoyelles"),
        ("7", "Beauregard"),
        ("8", "Bienville"),
        ("9", "Bossier"),
        ("10", "Caddo"),
        ("11", "Calcasieu"),
        ("12", "Caldwell"),
        ("13", "Cameron"),
        ("14", "Catahoula"),
        ("15", "Claiborne"),
        ("16", "Concordia"),
        ("17", "De Soto"),
        ("18", "East Baton Rouge"),
        ("19", "East Carroll"),
        ("20", "East Feliciana"),
        ("21", "Evangeline"),
        ("22", "Franklin"),
        ("23", "Grant"),
        ("24", "Iberia"),
        ("25", "Iberville"),
        ("26", "Jackson"),
        ("27", "Jefferson"),
        ("28", "Jefferson Davis"),
        ("29", "Lafayette"),
        ("30", "Lafourche"),
        ("31", "La Salle"),
        ("32", "Lincoln"),
        ("33", "Livingston"),
        ("34", "Madison"),
        ("35", "Morehouse"),
        ("36", "Natchitoches"),
        ("37", "Orleans"),
        ("38", "Ouachita"),
        ("39", "Plaquemines"),
        ("40", "Pointe Coupee"),
        ("41", "Rapides"),
        ("42", "Red River"),
        ("43", "Richland"),
        ("44", "Sabine"),
        ("45", "St. Bernard"),
        ("46", "St. Charles"),
        ("47", "St. Helena"),
        ("48", "St. James"),
        ("49", "St. John the Baptist"),
        ("50", "St. Landry"),
        ("51", "St. Martin"),
        ("52", "St. Mary"),
        ("53", "St. Tammany"),
        ("54", "Tangipahoa"),
        ("55", "Tensas"),
        ("56", "Terrebonne"),
        ("57", "Union"),
        ("58", "Vermilion"),
        ("59", "Vernon"),
        ("60", "Washington"),
        ("61", "Webster"),
        ("62", "West Baton Rouge"),
        ("63", "West Carroll"),
        ("64", "West Feliciana"),
        ("65", "Winn"),
    )
    MALE = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )
    SINGLE = 'S'
    MARRIED = 'M'
    DIVORCED = 'D'
    WIDOWED = 'W'
    OTHER = 'O'
    MARITAL_STATUS_CHOICES = (
        (SINGLE, 'Single'),
        (MARRIED, 'Married'),
        (DIVORCED, 'Divorced'),
        (WIDOWED, 'Widowed'),
        (OTHER, 'Other')
    )
    CCR = 'C'
    ESL = 'E'
    ELEARN = 'D'
    SUCCESS = 'S'
    ACE = 'A'
    PROGRAM_CHOICES = (
        (CCR, "College and Career Readiness - HiSET Prep Classes"),
        (ESL, "Beginning English Language Classes"),
        (ELEARN, "Online Classes"),
        (ACE, "ACE Program"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.PROTECT,
        related_name='student',
        verbose_name=_("user")
    )
    intake_date = models.DateField(
        null=True,
        blank=True,
        default=date.today
    )
    WRU_ID = models.CharField(
        null=True,
        blank=True,
        max_length=7
    )
    AEP_ID = models.CharField(
        unique=True,
        max_length=8,
        default=make_AEP_ID
    )
    other_ID = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Other ID, Passport #, Visa info, etc.")
    )
    US_citizen = models.BooleanField(
        default=False,
        verbose_name=_("US Citizen")
    )
    hispanic_latino = models.BooleanField(
        default=False,
        verbose_name=_("Hispanic/Latino"),
    )
    amer_indian = models.BooleanField(
        default=False,
        verbose_name=_("American Indian or Alaska Native")
    )
    asian = models.BooleanField(
        default=False,
        verbose_name=_("Asian")
    )
    black = models.BooleanField(
        default=False,
        verbose_name=_("Black or African American")
    )
    white = models.BooleanField(
        default=False,
        verbose_name=_("White")
    )
    pacific_islander = models.BooleanField(
        default=False,
        verbose_name=_("Native Hawaiian or Pacific Islander")
    )
    prior_registration = models.BooleanField(
        default=False,
        verbose_name=_("Have you registered for this program before?")
    )
    program = models.CharField(
        max_length=1,
        choices=PROGRAM_CHOICES,
        default='C'
    )
    parish = models.CharField(
        max_length=2,
        choices=PARISH_CHOICES,
        default='37'
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default='F'
    )
    marital_status = models.CharField(
        max_length=1,
        choices=MARITAL_STATUS_CHOICES,
        default='S',
        verbose_name=_('Marital Status')
    )
    native_language = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Native Language")
    )
    country = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Country of Highest Education")
    )

    def has_WRU_ID(self):
        pass

    def get_active_classes(self):
        pass

    def get_completed_classes(self):
        pass

    def get_all_classes(self):
        pass

    def get_absolute_url(self):
        return reverse('people:student detail', kwargs={'slug': self.slug})


class Staff(Profile):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        related_name='staff',
        verbose_name=_("user"))

    bio = models.TextField(blank=True, max_length=4000)

    def get_active_classes(self):
        pass

    def get_all_courses(self):
        pass

    def get_absolute_url(self):
        return reverse('people:staff detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name_plural = 'staff'


class WIOA(models.Model):

    EMPLOYMENT_STATUS_CHOICES = (
        ("1", "Employed"),
        ("2", "Unemployed"),
        ("3", "Unemployed - Not looking for work"),
        ("4", "Not in labor force"),
        ("5", "Employed, but recieved notice of termination or Military seperation is pending"),
        ("6", "Not in labor force and/or not looking for work"),
    )
    MIGRANT_SEASONAL_STATUS_CHOICES = (
        ("1", "Seasonal Farmworker"),
        ("2", "Migrant and Seasonal Farmworker"),
        ("3", "A Dependant of a Seasonal, or Migrant and Seasonal Farmworker"),
        ("4", "No"),
    )
    YES_NO_UNKNOWN = (
        ("1", "Yes"),
        ("2", "No"),
        ("3", "Unknown"),
    )
    YES_NO = (
        ("", "Please Select"),
        ("1", "Yes"),
        ("2", "No"),
    )
    ONE_STOP_CHOICES = (
        ("1", "Yes, Local Formula"),
        ("2", "Yes, Statewide"),
        ("3", "Yes, Both Local and Statewide"),
    )
    VOCATIONAL_REHAB_CHOICES = (
        ("", "Please Select"),
        ("1", "Vocational Rehabilitation"),
        ("2", "Vocational Rehabilitation and Employment, Statewide"),
        ("3", "Both, VR and VR&E"),
        ("4", "No"),
    )
    SCHOOL_STATUS_CHOICES = (
        ("", "Please Select"),
        ("1", "In-School, H.S. or less"),
        ("2", "In-School, Alternative School"),
        ("3", "In-School, Post H.S."),
        ("4", "Not attending school or H.S. dropout"),
        ("5", "Not attending school; H.S. graduate"),
        ("6", "Not attending school; within age of compulsory school attendance"),
    )
    TRAINING_TYPE_CHOICES = (
        ("1", "On the Job Training"),
        ("2", "Skill Upgrading"),
        ("3", "Entrepreneurial Training (non-WIOA Youth)"),
        ("4", "ABE or ESL in conjunction with Training (non-TAA funded)"),
        ("5", "Customized Training"),
        ("6", "Other Occupational Skills Training"),
        ("7", "Remedial Training (ABE/ESL – TAA only)"),
        ("8", "Prerequisite Training"),
        ("9", "Registered Apprenticeship"),
        ("10", "Youth Occupational Skills Training"),
        ("11", "Other Non-Occupational-Skills Training"),
        ("0", "No Training Service"),
    )
    PROGRAM_OF_STUDY_CHOICES = (
        ("1", "A program of study leading to an industry-recognized certificate or certification"),
        ("2", "A program of study leading to a certificate of completion of an apprenticeship"),
        ("3", "A program of study leading to a license recognized by the State involved or the Federal Government"),
        ("4", "A program of study leading to an associate degree"),
        ("5", "A program of study leading to a baccalaureate degree"),
        ("6", "A program of study leading to a community college certificate of completion"),
        ("7", "A program of study leading to a secondary school diploma or its equivalent"),
        ("8", "A program of study leading to employment"),
        ("9", "A program of study leading to a measureable skills gain leading to a credentiacredential or employmentment"),
        ("10", "Youth Occupational Skills Training"),
    )
    HIGHEST_COMPLETED_CHOICES = (
        ("1", "NO FORMAL SCHOOL"),
        ("2", "COMPLETED 1 YEAR"),
        ("3", "COMPLETED 2 YEARS"),
        ("4", "COMPLETED 3 YEARS"),
        ("5", "COMPLETED 4 YEARS"),
        ("6", "COMPLETED 5 YEARS"),
        ("7", "COMPLETED 6 YEARS"),
        ("8", "COMPLETED 7 YEARS"),
        ("9", "COMPLETED 8 YEARS"),
        ("10", "COMPLETED 9 YEARS"),
        ("11", "COMPLETED 10 YEARS"),
        ("12", "COMPLETED 11 YEARS"),
        ("13", "COMPLETED 12 YEARS (HS DIPLOMA NOT EARNED)"),
        ("14", "COMPLETED 13 YEARS"),
        ("15", "COMP 14 YEARS/ASSC DEG/TECHNICAL DIPLOMA"),
        ("16", "COMPLETED 15 YEARS"),
        ("17", "COMPLETED BACHELOR DEGREE"),
        ("18", "COMPLETED BEYOND BACHELOR DEGREE"),
        ("19", "HIGH SCHOOL EQUIVALENCY"),
        ("20", "CERTIFICATE OF ATTENDANCE OR COMPLETION (HS ONLY)"),
        ("21", "POST SECONDARY DEGREE/CERTIFICATE EARNED"),
        ("22", "COMPLETED 12 YEARS (HS DIPLOMA EARNED)"),
    )
    COMPLETED_AT_ENTRY_CHOICES = (
        ("1", "NO SCHOOL GRADE COMPLETED"),
        ("2", "COMPLETED 1 YEAR"),
        ("3", "COMPLETED 2 YEARS"),
        ("4", "COMPLETED 3 YEARS"),
        ("5", "COMPLETED 4 YEARS"),
        ("6", "COMPLETED 5 YEARS"),
        ("7", "COMPLETED 6 YEARS"),
        ("8", "COMPLETED 7 YEARS"),
        ("9", "COMPLETED 8 YEARS"),
        ("10", "COMPLETED 9 YEARS"),
        ("11", "COMPLETED 10 YEARS"),
        ("12", "COMPLETED 11 YEARS"),
        ("13", "COMPLETED 12 YEARS"),
    )
    SCHOOL_LOCATION_CHOICES = (
        ("", "Please Select"),
        ("1", "US Based"),
        ("2", "Non-US Based"),
    )

    student = models.OneToOneField(
        Student,
        models.CASCADE,
        related_name='WIOA'
    )
    current_employment_status = models.CharField(
        max_length=2,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default="2",
        verbose_name=_("Current Employment Status")
    )
    employer = models.CharField(
        max_length=25,
        blank=True,
        verbose_name=_("Employer")
    )
    occupation = models.CharField(
        max_length=25,
        blank=True,
        verbose_name=_("Employer")
    )
    migrant_seasonal_status = models.CharField(
        max_length=2,
        choices=MIGRANT_SEASONAL_STATUS_CHOICES,
        default="4",
        verbose_name=_("Migrant and Seasonal Farmworker Status")
    )
    long_term_unemployed = models.BooleanField(
        default=False,
        verbose_name=_("Long-term Unemployed"),
        help_text=_("More than 27 consecutive weeks")
    )
    single_parent = models.BooleanField(
        default=False,
        verbose_name=_("Single Parent")
    )
    public_assistance = models.BooleanField(
        default=False,
        verbose_name=_("Public Assistance")
    )
    rural_area = models.BooleanField(
        default=False,
        verbose_name=_("Rural Area")
    )
    displaced_homemaker = models.BooleanField(
        default=False,
        verbose_name=_("Displaced Homemaker")
    )
    dislocated_worker = models.BooleanField(
        default=False,
        verbose_name=_("Dislocated Worker")
    )
    cult_barriers_hind_emp = models.BooleanField(
        default=False,
        verbose_name=_("Cultural Barriers Hindering Employment")
    )
    in_foster_care = models.BooleanField(
        default=False,
        verbose_name=_("In Foster Care")
    )
    aged_out_foster_care = models.BooleanField(
        default=False,
        verbose_name=_("Aged out of Foster Care")
    )
    exhaust_tanf = models.BooleanField(
        default=False,
        verbose_name=_("Exhausting TANF Within 2 Years")
    )
    disability_status = models.CharField(
        max_length=1,
        choices=YES_NO_UNKNOWN,
        blank=True
    )
    job_corps = models.CharField(
        max_length=1,
        choices=YES_NO_UNKNOWN,
        blank=True
    )
    youth_build = models.CharField(
        max_length=1,
        choices=YES_NO_UNKNOWN,
        blank=True
    )
    low_income = models.BooleanField(
        default=False,
        verbose_name=_("Low Income")
    )
    low_literacy = models.BooleanField(
        default=False,
        verbose_name=_("Low Literacy")
    )
    # Tick Checkboxes
    # A
    recieves_public_assistance = models.BooleanField(
        default=False,
    )
    # B
    low_family_income = models.BooleanField(
        default=False,
    )
    # C
    free_lunch_youth = models.BooleanField(
        default=False,
    )
    # D
    state_payed_foster = models.BooleanField(
        default=False,
    )
    # E
    disabled_in_poverty = models.BooleanField(
        default=False,
    )
    # F
    homeless = models.BooleanField(
        default=False,
    )
    # G
    youth_in_high_poverty_area = models.BooleanField(
        default=False,
    )
    # Ex Offender
    # A
    subject_of_criminal_justice = models.BooleanField(
        default=False,
    )
    # B
    arrest_record_employment_barrier = models.BooleanField(
        default=False,
    )
    # Homeless Individual
    # A
    lacks_adequate_reisdence = models.BooleanField(
        default=False,
    )
    # B
    irregular_sleep_accomodation = models.BooleanField(
        default=False,
    )
    # C
    migratory_child = models.BooleanField(
        default=False,
    )
    # D
    runaway_youth = models.BooleanField(
        default=False,
        )
