from datetime import date, datetime
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
        ("D", "Father"),
        ("M", "Mother"),
        ("S", "Spouse"),
        ("B", "Sibling"),
        ("F", "Friend"),
        ("G", "Legal Guardian"),
        ("O", "Other")
    )
    phone = models.CharField(
        max_length=20,
        verbose_name=_("Phone Number"),
    )
    alt_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Alternate Phone Number"),
    )
    street_address_1 = models.CharField(
        max_length=60,
        verbose_name=_("Street Address 1"),
    )
    street_address_2 = models.CharField(
        max_length=60,
        blank=True,
        verbose_name=("Street Address 2"))
    city = models.CharField(
        max_length=30,
    )
    state = models.CharField(
        max_length=2,
        choices=STATE_CHOICES,
        default="LA"
    )
    zip_code = models.CharField(
        max_length=10,
        verbose_name=_("Zip Code")
    )
    dob = models.DateField(
        verbose_name=_("Date of Birth")
    )
    emergency_contact = models.CharField(
        max_length=60,
        blank=True,
        verbose_name=_("Emergency Contact Full Name")
    )
    ec_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Their Phone Number")
    )
    ec_email = models.EmailField(
        max_length=40,
        blank=True,
        verbose_name=_("Their Email Address")
    )
    ec_relation = models.CharField(
        max_length=1,
        choices=EC_RELATIONS_CHOICES,
        default='O',
        verbose_name=_("Their Relationship to You")
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
        verbose_name=_("State ID, Passport #, Visa info, etc.")
    )
    other_ID_name = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('What kind of ID is this?')
    )
    US_citizen = models.BooleanField(
        default=False,
        verbose_name=_("US Citizen")
    )
    prior_registration = models.BooleanField(
        default=False,
        verbose_name=_("Returning Student"),
        help_text=_("Have you registered with this program in the past?")
    )
    program = models.CharField(
        max_length=1,
        choices=PROGRAM_CHOICES,
        default='C'
    )
    ccr_app = models.BooleanField(
        default=False,
        verbose_name=_("CCR")
    )
    esl_app = models.BooleanField(
        default=False,
        verbose_name=_("ESL")
    )
    ace_app = models.BooleanField(
        default=False,
        verbose_name=_("ACE")
    )
    e_learn_app = models.BooleanField(
        default=False,
        verbose_name=_("ELearn")
    )
    success_app = models.BooleanField(
        default=False,
        verbose_name=_("Success")
    )
    eng_boot_app = models.BooleanField(
        default=False,
        verbose_name=_("Eng. Boot")
    )
    math_boot_app = models.BooleanField(
        default=False,
        verbose_name=_("Math Boot")
    )
    accuplacer_app = models.BooleanField(
        default=False,
        verbose_name=_("Accuplacer")
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

    class Meta:
        ordering = ["user__last_name", "user__first_name"]

    def get_absolute_url(self):
        return reverse('people:student detail', kwargs={'slug': self.slug})

    def future_appts(self):
        return self.test_appointments.filter(
            event__start__gte=datetime.today()
        ).order_by('event__start')

    def active_classes(self):
        return self.classes.filter(
            status="A"
        ).order_by('-section__semester__end_date')

    def completed_classes(self):
        return self.classes.filter(
            status="C"
        ).order_by('-section__semester__end_date')

    def dropped_classes(self):
        return self.classes.filter(
            status="D"
        ).order_by('-section__semester__end_date')

    def current_classes(self):
        today = date.today()
        return self.classes.filter(section__semester__end_date__gte=today)

    def past_classes(self):
        today = date.today()
        return self.classes.filter(section__semester__end_date__lt=today)

    def all_classes(self):
        return self.classes.all()


class Staff(Profile):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        related_name='staff',
        verbose_name=_("user"))

    wru = models.CharField(blank=True, max_length=5)

    bio = models.TextField(blank=True, max_length=4000)

    g_suite_email = models.EmailField(
        blank=True,
        max_length=30
    )

    teacher = models.BooleanField(default=True)

    coach = models.BooleanField(default=False)

    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'staff'
        ordering = ["user__last_name", "user__first_name"]

    def get_absolute_url(self):
        return reverse('people:staff detail', kwargs={'slug': self.slug})

    def current_classes(self):
        today = date.today()
        return self.classes.filter(semester__end_date__gte=today)

    def past_classes(self):
        today = date.today()
        return self.classes.filter(semester__end_date__lt=today)


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
        ("1", "Yes"),
        ("2", "No"),
    )
    ONE_STOP_CHOICES = (
        ("1", "Yes, Local Formula"),
        ("2", "Yes, Statewide"),
        ("3", "Yes, Both Local and Statewide"),
        ("4", "No"),
    )
    VOCATIONAL_REHAB_CHOICES = (
        ("1", "Vocational Rehabilitation"),
        ("2", "Vocational Rehabilitation and Employment, Statewide"),
        ("3", "Both, VR and VR&E"),
        ("4", "No"),
    )
    SCHOOL_STATUS_CHOICES = (
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
    SID = models.CharField(
        max_length=11,
        blank=True,
        verbose_name="SSN",
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
    native_language = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Native Language - if not English")
    )
    country = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Country of Origin - if not US")
    )
    current_employment_status = models.CharField(
        max_length=2,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default="2",
        verbose_name=_("What is your current employment status")
    )
    employer = models.CharField(
        max_length=25,
        blank=True,
        verbose_name=_("Employer")
    )
    occupation = models.CharField(
        max_length=25,
        blank=True,
        verbose_name=_("Occupation")
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
        verbose_name=_("Are you a single parent?")
    )
    rural_area = models.BooleanField(
        default=False,
        verbose_name=_("Do you live in a rural area?")
    )
    displaced_homemaker = models.BooleanField(
        default=False,
        verbose_name=_("Are you a displaced homemaker?")
    )
    dislocated_worker = models.BooleanField(
        default=False,
        verbose_name=_("Are you a dislocated worker?")
    )
    cult_barriers_hind_emp = models.BooleanField(
        default=False,
        verbose_name=_(
            "Are there cultural barriers hindering your employment?"
        )
    )
    in_foster_care = models.BooleanField(
        default=False,
        verbose_name=_("Are you currently in foster care?")
    )
    aged_out_foster_care = models.BooleanField(
        default=False,
        verbose_name=_(
            "Have you aged out of foster care?"
        )
    )
    exhaust_tanf = models.BooleanField(
        default=False,
        verbose_name=_(
            "Are you recieving TANF assistance that ends within 2 years?"
        )
    )
    job_corps = models.CharField(
        max_length=1,
        choices=YES_NO_UNKNOWN,
        blank=True,
        verbose_name=_("Are you in Job Corps?")
    )
    youth_build = models.CharField(
        max_length=1,
        choices=YES_NO_UNKNOWN,
        blank=True,
        verbose_name=_("Are you in a Youth Build program?")
    )

    # Tick Checkboxes
    # A
    recieves_public_assistance = models.BooleanField(
        default=False,
        verbose_name=_("Do you recieve public assistance?")
    )
    # B
    low_family_income = models.BooleanField(
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
    lacks_adequate_residence = models.BooleanField(
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
    # Adult
    adult_one_stop = models.CharField(
        max_length=1,
        choices=ONE_STOP_CHOICES,
        default="4"
    )
    # Youth
    youth_one_stop = models.CharField(
        max_length=1,
        choices=ONE_STOP_CHOICES,
        default="4"
    )
    # Vocational Rehab
    voc_rehab = models.CharField(
        max_length=1,
        choices=VOCATIONAL_REHAB_CHOICES,
        default="4"
    )
    # Wagner Peyser Act
    wagner_peyser = models.CharField(
        max_length=1,
        choices=YES_NO_UNKNOWN,
        default="3"
    )
    # School Status at Participation
    school_status = models.CharField(
        max_length=1,
        choices=SCHOOL_STATUS_CHOICES,
        blank=True
    )
    recieved_training = models.CharField(
        max_length=1,
        choices=YES_NO,
        default="2")
    # Eligible Training Provider
    etp_name = models.CharField(
        max_length=30,
        blank=True
    )
    etp_program = models.CharField(
        max_length=2,
        blank=True,
        choices=PROGRAM_OF_STUDY_CHOICES,
    )
    etp_CIP_Code = models.CharField(
        max_length=20,
        blank=True
    )
    training_type_1 = models.CharField(
        max_length=2,
        blank=True,
        choices=TRAINING_TYPE_CHOICES
    )
    training_type_2 = models.CharField(
        max_length=2,
        blank=True,
        choices=TRAINING_TYPE_CHOICES
    )
    training_type_3 = models.CharField(
        max_length=2,
        blank=True,
        choices=TRAINING_TYPE_CHOICES
    )
    # Disability Details
    # Disability

    # ADHD
    adhd = models.BooleanField(
        default=False,
        verbose_name=_("ADHD")
    )
    # Autism
    autism = models.BooleanField(
        default=False,
        verbose_name=_("Autism")
    )
    # Deaf-blindness
    deaf_blind = models.BooleanField(
        default=False,
        verbose_name=_("Deaf-blindness")
    )
    # Deafness
    deaf = models.BooleanField(
        default=False,
        verbose_name=_("Deafness")
    )
    # Emotional Disturbance
    emotional_disturbance = models.BooleanField(
        default=False,
        verbose_name=_("Emotional Disturbance")
    )
    # Had an IEP in K-12
    k12_iep = models.BooleanField(
        default=False,
        verbose_name=_("Had an IEP in K-12")
    )
    # Hard of Hearing
    hard_of_hearing = models.BooleanField(
        default=False,
        verbose_name=_("Hard of Hearing")
    )
    # Intellectual Disability
    intellectual_disability = models.BooleanField(
        default=False,
        verbose_name=_("Intellectual Disability")
    )
    # Multiple Disabilities
    multiple_disabilities = models.BooleanField(
        default=False,
        verbose_name=_("Multiple Disabilities")
    )
    # Orthopedic Impairment
    orthopedic_impairment = models.BooleanField(
        default=False,
        verbose_name=_("Orthopedic Impairment")
    )
    # Other Health Impairment
    other_health_impairment = models.BooleanField(
        default=False,
        verbose_name=_("Other Health Impairment")
    )
    # Specific Learning Disability
    learning_disability = models.BooleanField(
        default=False,
        verbose_name=_("Specific Learning Disability")
    )
    # Speech or Language Impairment
    speech_or_lang_impairment = models.BooleanField(
        default=False,
        verbose_name=_("Speech or Language Impairment")
    )
    # Traumatic Brain Injury
    traumatic_brain_injury = models.BooleanField(
        default=False,
        verbose_name=_("Traumatic Brain Injury")
    )
    # Visual Impairment
    visual_impairment = models.BooleanField(
        default=False,
        verbose_name=_("Visual Impairment")
    )

    # Learning Disabled

    # Dyscalculia
    dyscalculia = models.BooleanField(
        default=False,
        verbose_name=_("Dyscalculia")
    )
    # Dysgraphia
    dysgraphia = models.BooleanField(
        default=False,
        verbose_name=_("Dysgraphia")
    )
    # Dyslexia
    dyslexia = models.BooleanField(
        default=False,
        verbose_name=_("Dyslexia")
    )
    # Related to Neurological Impairments
    neurological_impairments = models.BooleanField(
        default=False,
        verbose_name=_("Related to Neurological Impairments")
    )
    highest_level_completed = models.CharField(
        max_length=2,
        choices=HIGHEST_COMPLETED_CHOICES,
        default="1",
    )
    highet_level_at_entry = models.CharField(
        max_length=2,
        choices=COMPLETED_AT_ENTRY_CHOICES,
        default="1"
    )
    school_location = models.CharField(
        max_length=1,
        choices=SCHOOL_LOCATION_CHOICES,
        default="1"
    )

    class Meta:
        verbose_name_plural = "WIOA records"

    def __str__(self):
        return self.student.__str__()


class CollegeInterest(models.Model):

    YES_NO_MAYBE = (
        ('Y', 'Yes'),
        ('N', 'No'),
        ('C', "I don't know")
    )

    GED_HISET_CHOICES = (
        ('1', 'Yes, high school diploma'),
        ('2', 'Yes, high school equivalency'),
        ('3', 'No')
    )

    DEFAULT = 'D'
    REPAYMENT = 'R'
    PAID = 'P'
    OTHER = 'O'
    UNKNOWN = 'U'
    AID_STATUS_CHOICES = (
        (DEFAULT, 'Default'),
        (REPAYMENT, 'Repayment'),
        (PAID, 'Paid in full'),
        (UNKNOWN, "I don't know"),
        (OTHER, 'Other')
    )

    FULL_TIME = 'F'
    PART_TIME = 'P'
    LOOKING = 'L'
    NOT_LOOKING = 'N'
    EMPLOYMENT_STATUS_CHOICES = (
        (FULL_TIME, "Yes, I’m employed full-time (more than 30 hours per week)."),
        (PART_TIME, "Yes, I’m employed part-time (less than 30 hours per week)."),
        (LOOKING, "No, but I’m looking for work."),
        (NOT_LOOKING, "No, and I’m not looking for work right now.")

    )

    student = models.OneToOneField(
        Student,
        models.CASCADE,
        related_name='college_interest'
    )

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='college_interest_records'
    )

    ged_hiset = models.CharField(
        max_length=1,
        choices=GED_HISET_CHOICES,
        verbose_name=_('Do you have your high school diploma or high school equivalency (GED/HiSET)?')
    )

    current_adult_ed = models.BooleanField(
        default=True,
        verbose_name=_('Check this box if you are currently attending adult education classes')
    )

    adult_ed_location = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Where?')
    )

    bpcc = models.BooleanField(
        default=False,
        verbose_name=_('Bossier Parish Community College (BPCC)')
    )

    brcc = models.BooleanField(
        default=False,
        verbose_name=_('Baton Rouge Community College (BRCC)')
    )

    ctcc = models.BooleanField(
        default=False,
        verbose_name=_('Central Louisiana Technical Community College (CTCC)')
    )

    dcc = models.BooleanField(
        default=False,
        verbose_name=_('Delgado Community College')
    )

    ldcc = models.BooleanField(
        default=False,
        verbose_name=_('Louisiana Delta Community College')
    )

    ftcc = models.BooleanField(
        default=False,
        verbose_name=_('Fletcher Technical Community College')
    )

    ntcc = models.BooleanField(
        default=False,
        verbose_name=_('Northshore Technical Community College')
    )

    ncc = models.BooleanField(
        default=False,
        verbose_name=_('Nunez Community College')
    )

    nltc = models.BooleanField(
        default=False,
        verbose_name=_('Northwest Louisiana Technical College')
    )

    rpcc = models.BooleanField(
        default=False,
        verbose_name=_('River Parishes Community College (RPCC)')
    )

    scl = models.BooleanField(
        default=False,
        verbose_name=_('South Central Louisiana Technical College (SCL)')
    )

    slcc = models.BooleanField(
        default=False,
        verbose_name=_('South Louisiana Community College')
    )

    sowela = models.BooleanField(
        default=False,
        verbose_name=_('Southwest Louisiana Technical Community College (SOWELA)')
    )

    lola = models.CharField(
        max_length=15,
        blank=True,
        verbose_name=_('Do you know your LOLA number?')
    )

    other_college = models.BooleanField(
        default=False,
        verbose_name=_('Have you ever attended college before (anywhere)?')
    )

    other_college_location = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_('Where was that?')
    )

    other_college_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Did you enroll under a different name than the one you gave us?')
    )

    prev_balance = models.CharField(
        max_length=1,
        choices=YES_NO_MAYBE,
        blank=True,
        verbose_name=_("If you've attended college before, do you owe a balance to that college?")
    )

    financial_aid = models.CharField(
        max_length=1,
        choices=YES_NO_MAYBE,
        blank=True,
        verbose_name=_('Have you ever used financial aid (student loans or grants) before?')
    )

    aid_status = models.CharField(
        max_length=1,
        choices=AID_STATUS_CHOICES,
        blank=True,
        verbose_name=_('If you have used financial aid before, what is your current financial aid status?')
    )

    nslds_notes = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('NLDS notes from ACE Staff:')
    )

    fafsa1617 = models.BooleanField(
        default=False,
        verbose_name='2016-2017'
    )
    fafsa1718 = models.BooleanField(
        default=False,
        verbose_name='2017-2018'
    )
    fafsa1819 = models.BooleanField(
        default=False,
        verbose_name='2018-2019'
    )

    delgado_classes = models.CharField(
        max_length=400,
        blank=True,
        verbose_name=_(
            "If you've taken college classes at Delgado,"
            " please list the classes you took and when,"
            " to the best of your knowledge."
            )
    )

    workforce_training = models.BooleanField(
        default=False,
        verbose_name=_('Have you ever take any workforce training classes?')
    )

    workforce_training_desc = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('What kind of workforce training classes?')
    )

    serv_safe = models.BooleanField(
        default=False,
        verbose_name="ServSafe Manager's Level Certification"
    )

    nccer = models.BooleanField(
        default=False,
        verbose_name='NCCER Core Certification'
    )

    ic3 = models.BooleanField(
        default=False,
        verbose_name='Internet and Computing Core (IC3) Certification'
    )

    first_aid = models.BooleanField(
        default=False,
        verbose_name='First Aid'
    )

    cpr = models.BooleanField(
        default=False,
        verbose_name='CPR'
    )

    employment_status = models.CharField(
        max_length=1,
        choices=EMPLOYMENT_STATUS_CHOICES,
        verbose_name=_('Are you currently employed?')
    )

    work_schedule = models.CharField(
        max_length=400,
        blank=True,
        verbose_name=_('What is your usual work schedule like?')
    )

    career_goals = models.CharField(
        max_length=2000,
        blank=True,
        verbose_name=_('What kind of career would you like to have when you finish school?')
    )

    notes = models.CharField(
        max_length=2000,
        blank=True
    )

    class Meta:
        verbose_name_plural = "College Interest Records"

    def __str__(self):
        return " | ".join([self.student.WRU_ID, self.student.__str__()])

    def get_absolute_url(self):
        return reverse('people:college interest detail', kwargs={'slug': self.student.slug})