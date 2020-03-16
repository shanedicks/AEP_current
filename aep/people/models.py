import requests
import bs4
from datetime import datetime
from django.apps import apps
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from core.utils import make_slug, make_AEP_ID, state_session


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
    first_name = models.CharField(
        max_length=30,
        verbose_name=_("First Name"),
        blank=True
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name=_("Last Name"),
        blank=True
    )
    email = models.EmailField(
        max_length=60,
        verbose_name=_("Email Address"),
        blank=True
    )
    alt_email = models.EmailField(
        max_length=60,
        verbose_name=_("Alternate Email Address"),
        blank=True
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
        return '{0} {1}'.format(self.first_name, self.last_name)


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
        verbose_name=_("user"),
        null=True,
        blank=True
    )
    intake_date = models.DateField(
        null=True,
        blank=True,
        default=timezone.localdate()
    )
    WRU_ID = models.CharField(
        null=True,
        blank=True,
        max_length=20
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
    )
    marital_status = models.CharField(
        max_length=1,
        choices=MARITAL_STATUS_CHOICES,
        default='S',
        verbose_name=_('Marital Status')
    )
    partner = models.CharField(
        max_length=40,
        blank=True
    )
    duplicate_of = models.ForeignKey(
        'self',
        models.CASCADE,
        null=True,
        blank=True,
        related_name='duplicated_by'
    )
    duplicate = models.BooleanField(
        default=False
    )
    dupl_date = models.DateField(
        null=True,
        blank=True
    )
    notes = models.TextField(
        blank=True
    )

    PENDING = 'P'
    INCOMPLETE = 'I'
    COMPLETE = 'C'

    OFFICE_CHOICES = (
        (PENDING, 'Pending'),
        (INCOMPLETE, 'Incomplete'),
        (COMPLETE, 'Complete')
    )

    paperwork = models.CharField(
        max_length=1,
        blank=True,
        choices=OFFICE_CHOICES,
        default=PENDING
    )

    folder = models.CharField(
        max_length=1,
        blank=True,
        choices=OFFICE_CHOICES,
        default=PENDING
    )

    orientation = models.CharField(
        max_length=1,
        blank=True,
        choices=OFFICE_CHOICES,
        default=PENDING
    )

    class Meta:
        ordering = ["last_name", "first_name"]

    def get_absolute_url(self):
        return reverse('people:student detail', kwargs={'slug': self.slug})

    def future_appts(self):
        return self.test_appointments.filter(
            event__start__gte=timezone.now()
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
        today = timezone.localdate()
        return self.classes.filter(section__semester__end_date__gte=today)

    def past_classes(self):
        today = timezone.localdate()
        return self.classes.filter(
            section__semester__end_date__lt=today
        ).order_by(
            '-section__semester__end_date'
        )

    def all_classes(self):
        return self.classes.all()

    def latest_class_start(self):
        return self.classes.latest('section__semester__start_date').section.semester.start_date

    def last_attendance(self):
        attendance = apps.get_model('sections', 'Attendance').objects.filter(enrollment__student=self, attendance_type='P')
        return attendance.latest('attendance_date').attendance_date

    def testify(self):
        TestHistory = apps.get_model('assessments', 'TestHistory')
        if TestHistory.objects.filter(student=self).exists():
            pass
        else:
            if self.WRU_ID not in [None, 'No ID']:
                TestHistory.objects.create(student=self, student_wru=self.WRU_ID)

    def track(self):
        Paperwork = apps.get_model('people', 'Paperwork')
        try: 
            Paperwork.objects.create(student=self)
        except:
            pass

    def create_elearn_record(self):
        Elearn = apps.get_model('coaching', 'ElearnRecord')
        if Elearn.objects.filter(student=self).exists():
            pass
        else:
            Elearn.objects.create(
                student=self,
                intake_date=datetime.today()
            )


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
        max_length=50
    )

    teacher = models.BooleanField(default=True)

    coach = models.BooleanField(default=False)

    active = models.BooleanField(default=True)

    full_time = models.BooleanField(default=False)

    partner = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'staff'
        ordering = ["last_name", "first_name"]

    def get_absolute_url(self):
        return reverse('people:staff detail', kwargs={'slug': self.slug})

    def current_classes(self):
        today = timezone.localdate()
        return self.classes.filter(
            semester__end_date__gte=today
        ).order_by(
            '-monday',
            'start_time'
        )

    def past_classes(self):
        today = timezone.localdate()
        return self.classes.filter(
            semester__end_date__lt=today
        ).order_by(
            '-semester__end_date',
            '-monday',
            'start_time'
        )

class Paperwork(models.Model):

    student = models.OneToOneField(
        Student,
        models.CASCADE,
        related_name='student_paperwork'
    )

    ferpa = models.BooleanField(
        default = False,
        verbose_name = 'FERPA'
    )

    test_and_comp = models.BooleanField(
        default = False,
        verbose_name = 'Test and Computer Usage Policy'
    )

    contract = models.BooleanField(
        default = False,
        verbose_name = 'Student Contract'
    )

    disclosure = models.BooleanField(
        default = False,
        verbose_name = 'Self-Disclosure Form'
    )

    lsi = models.BooleanField(
        default = False,
        verbose_name = 'Learning Style Inventory'
    )

    writing = models.BooleanField(
        default = False,
        verbose_name = 'Writing Sample'
    )

    pic_id = models.BooleanField(
        default = False,
        verbose_name = 'Picture ID'
    )

    class Meta:
        verbose_name_plural = 'paperwork'
        ordering = ['student__last_name', 'student__first_name']

    def __str__(self):
        return '{0} Paperwork'.format(self.student)

def convert_date_format(date_string):
    date_input = datetime.strptime(date_string, "%m/%d/%y")
    return datetime.strftime(date_input, "%m/%d/%Y")


def get_SID(sid):
    return "".join(sid.split("-"))

def get_age_at_intake(dob, intake_date):
    diff = intake_date - dob
    age = diff.days // 365
    return age


def citizen(input):
    if input == 1:
        cit = "true"
    else:
        cit = "false"
    return cit


def marital(input):
    statuses = {
        "S": "1",
        "M": "2",
        "D": "3",
        "W": "4",
        "O": "5"
    }
    return statuses[input]


def gender(input):
    genders = {
        "M": "2",
        "F": "1"
    }
    return genders[input]


def state(input):
    states = {
        "AL": "2",
        "AK": "1",
        "AZ": "4",
        "AR": "3",
        "CA": "5",
        "CO": "6",
        "CT": "7",
        "DC": "8",
        "DE": "9",
        "FL": "10",
        "GA": "11",
        "HI": "12",
        "ID": "14",
        "IL": "15",
        "IN": "16",
        "IA": "13",
        "KS": "17",
        "KY": "18",
        "LA": "19",
        "ME": "22",
        "MA": "20",
        "MD": "21",
        "MI": "23",
        "MN": "24",
        "MS": "26",
        "MO": "25",
        "MT": "27",
        "NE": "30",
        "NV": "34",
        "NH": "31",
        "NJ": "32",
        "NM": "33",
        "NY": "35",
        "NC": "28",
        "ND": "29",
        "OH": "36",
        "OK": "37",
        "OR": "38",
        "PA": "39",
        "RI": "40",
        "SC": "41",
        "SD": "42",
        "TN": "43",
        "TX": "44",
        "UT": "45",
        "VA": "46",
        "VT": "47",
        "WA": "48",
        "WV": "50",
        "WI": "49",
        "WY": "51"
    }
    return states[input]


def email_status(input):
    if input != "":
        return "true"
    else:
        return "false"


def true_false(input):
    if input is True:
        return "true"
    else:
        return "false"


def hl_tf(input):
    if input is True:
        return "True"
    else:
        return "False"


def primary_program(student):
    if student.success_app:
        program = '14'
    elif student.ace_app:        
        program = '15'
    elif student.e_learn_app:
        program = '12'
    elif student.esl_app:
        program = '16'
    else:
        program = "1"
    return program


def secondary_program(student):
    program = ""
    if student.ccr_app:
        program = '8'
    if student.esl_app:
        program = '6'
    return program


def esl(student):
    if student.esl_app:
        return "true"
    else:
        return "false"


def employment_status(input):
    emp = {
        "1": "1_EM",
        "2": "3_UE",
        "3": "4_UNL",
        "4": "5_NLF",
        "5": "1_EM",
        "6": "5_NLF"
    }
    return emp[input]


def migrant(input):
    mig = {
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 0,
    }
    return mig[input]


def one_stop(input):
    o = {
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 0
    }
    return o[input]


def y_n_u(input):
    y = {
        "": 9,
        "1": 1,
        "2": 0,
        "3": 9
    }
    return y[input]


def school_status(input):
    status = {
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6
    }
    return status[input]


def dislocated(input):
    if input is True:
        return 1
    else:
        return 0


def voc_rehab(input):
    v = {
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 0
    }
    return v[input]


def wru_search(session, search_dict):
    s = session.get(
        'https://workreadyu.lctcs.edu/Student',
        data=search_dict
    )
    p = bs4.BeautifulSoup(
        s.text,
        "html.parser"
    )
    try:
        return p.select("table.Webgrid > tbody > tr > td")[9].text.encode('utf-8')
    except IndexError:
        return 'No ID'


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
        default=2,
        verbose_name=_("Are you in Job Corps?")
    )
    youth_build = models.CharField(
        max_length=1,
        choices=YES_NO_UNKNOWN,
        blank=True,
        default=2,
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
        default="4",
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

    def check_for_state_id(self, session):

        search = {
            'LastNameTextBox': self.student.last_name,
            'FirstNameTextBox': self.student.first_name,
            'Status': -1,
            'AgeSearchType': 1,
            'AgeFromInequality': 4,
            'AgeFromTextBox': get_age_at_intake(self.student.dob, self.student.intake_date),
            'btnFilter': 'Filter List'
        }

        wru = wru_search(session, search)

        if wru == 'No ID':
            if self.SID:
                search = {
                    'SSNTextBox': get_SID(self.SID),
                    'Status': -1,
                    'btnFilter': 'Filter List'
                }
                wru = wru_search(session, search)

        if wru != 'No ID':
            wru = b'x' + wru
            wru = wru.decode('ascii')

        self.student.WRU_ID = wru
        self.student.save()

    def send_to_state(self, session):

        student = {
            "hdnRoleType": "2",
            "hdnInactiveStateKey": ",2,3,4,5,",
            "hdnInactiveProg": ",7,13,",
            "hdnInactiveEmpStat": ",4_UNL, 5_NLF,",
            "IntakeOnlyProgram": "19",
            "IsIntakeOnly": "true",
            "EnrollPStat.IntakeDate": self.student.intake_date,
            "FY": "7",
            "lblCurrentFY": "5",
            "FYBginDate": "7/1/2019",
            "FYEndDate": "6/30/2020",
            "hdnProviderId": "DELGADO COMMUNITY COLLEGE",
            "StudentId": "0",
            "SSN": get_SID(self.SID),
            "LastName": self.student.last_name,
            "FirstName": self.student.first_name,
            "MiddleInitial": "",
            "DateOfBirth": self.student.dob,
            "Age": get_age_at_intake(self.student.dob, self.student.intake_date),
            "USCitizen": citizen(self.student.US_citizen),
            "MaritalStatusId": marital(self.student.marital_status),
            "Gender": gender(self.student.gender),
            "OtherID": "",
            "Suffix": "",
            "Address.Street1": self.student.street_address_1,
            "Address.Street2": self.student.street_address_2,
            "Address.City": self.student.city,
            "Address.StateId": state(self.student.state),
            "Address.Zip": self.student.zip_code,
            "Address.AddressTypeId": "1",
            "Address.Status": "true",
            "Address.Status": "false",
            "Address.VTCountyId": self.student.parish,
            "Telephone.PrimaryPhoneNumber": self.student.phone,
            "Telephone.PrimaryPhoneTypeId": "3",
            "Telephone.PrimaryPhoneStatus": "true",
            "Telephone.PrimaryPhoneStatus": "false",
            "Telephone.AlternativePhoneNumber1": "",
            "Telephone.AlternativePhoneType1Id": "",
            "Telephone.AlternativePhoneStatus1": "false",
            "Telephone.AlternativePhoneNumber2": "",
            "Telephone.AlternativePhoneType2Id": "",
            "Telephone.AlternativePhoneStatus2": "false",
            "Telephone.AlternativePhoneNumber3": "",
            "Telephone.AlternativePhoneTypeId3": "",
            "Telephone.AlternativePhoneNumberStatus3": "false",
            "Emergency.LastName": "",
            "Emergency.FirstName": "",
            "Emergency.RelationshipId": "",
            "Emergency.Telephone1": "",
            "Emergency.Telephone2": "",
            "Email.Email1": self.student.email,
            "Email.EmailTypeId": "1",
            "Email.EmailStatus": email_status(self.student.email),
            "HispanicLatino": hl_tf(self.hispanic_latino),
            "Ethnicity_1": true_false(self.amer_indian),
            "Ethnicity_2": true_false(self.asian),
            "Ethnicity_3": true_false(self.black),
            "Ethnicity_5": true_false(self.white),
            "Ethnicity_4": true_false(self.pacific_islander),
            "Program.ProgramTypeId": primary_program(self.student),
            "Program.StateKeyword": "",
            "Program.SecondaryProgram1TypeId": secondary_program(self.student),
            "ESLStudent": esl(self.student),
            "Program.Keyword": "",
            "Program.SecondaryProgram2TypeId": "",
            "Program.NativeLanguage": self.native_language,
            "Program.SecondaryProgram3TypeId": "",
            "Program.SecondaryProgram4TypeId": "",
            "Program.CountryOfHighestEducation": self.country,
            "Program.PastEnrollment": true_false(self.student.prior_registration),
            "Program.PastEnrollCollege": "",
            "EmploymentStatusId": employment_status(self.current_employment_status),
            "EnrollPStat.EmploymentLocation": self.employer,
            "EnrollPStat.Occupation": self.occupation,
            "EnrollSStat.PublicAssistance": true_false(self.recieves_public_assistance),
            "EnrollSStat.RuralArea": true_false(self.rural_area),
            "EnrollSStat.LowIncome": true_false(self.low_family_income),
            "EnrollSStat.DisplayedHomemaker": true_false(self.displaced_homemaker),
            "EnrollSStat.SingleParent": true_false(self.single_parent),
            "EnrollSStat.DislocatedWorker": true_false(self.dislocated_worker),
            "StudentWIOADetail.MigrantAndSeasonalFarmworker": migrant(self.migrant_seasonal_status),
            "StudentWIOADetail.NNLongTermUnemployed": true_false(self.long_term_unemployed),
            "StudentWIOADetail.DislocatedWorker": dislocated(self.dislocated_worker),
            "StudentWIOADetail.NNCulturalBarriers": true_false(self.cult_barriers_hind_emp),
            "StudentWIOADetail.NNFostercareYouth": true_false(self.in_foster_care),
            "StudentWIOADetail.NNAgedOutFosterCare": true_false(self.aged_out_foster_care),
            "StudentWIOADetail.NNExhaustingTANFWithin2Years": true_false(self.exhaust_tanf),
            "StudentWIOADetail.IndividualWithDisability": "",
            "StudentWIOADetail.JobCorps": y_n_u(self.job_corps),
            "StudentWIOADetail.YouthBuild": y_n_u(self.youth_build),
            "StudentWIOADetail.NNLowLevelsOfLiteracy": "false",
            "StudentWIOADetail.NNRecievedAssistance": true_false(self.recieves_public_assistance),
            "StudentWIOADetail.NNIncomeBelowStandardIncomeLevel": true_false(self.low_family_income),
            "StudentWIOADetail.NNReceiveReducedPriceLunch": "false",
            "StudentWIOADetail.NNLowIncomeFosterChild": true_false(self.state_payed_foster),
            "StudentWIOADetail.NNLowIncomeIndividualWithDisability": true_false(self.disabled_in_poverty),
            "StudentWIOADetail.NNHomelessOrRunawayYouth": true_false(self.runaway_youth),
            "StudentWIOADetail.NNLivingInHighPovertyArea": true_false(self.youth_in_high_poverty_area),
            "StudentWIOADetail.NNSubjectToCriminalJusticeProcess": true_false(self.subject_of_criminal_justice),
            "StudentWIOADetail.NNBarriersToEmployment": true_false(self.arrest_record_employment_barrier),
            "StudentWIOADetail.NNLacksFixedNighttimeResidence": true_false(self.lacks_adequate_residence),
            "StudentWIOADetail.NNNighttimeResidenceNotForHumans": true_false(self.irregular_sleep_accomodation),
            "StudentWIOADetail.NNMigratoryChild": true_false(self.migratory_child),
            "StudentWIOADetail.NNBelow18AndAbsetFromHome": true_false(self.runaway_youth),
            "StudentWIOADetail.Adult": one_stop(self.adult_one_stop),
            "StudentWIOADetail.AdultDateofLastService": "",
            "StudentWIOADetail.AdultProviderName": "",
            "StudentWIOADetail.AdultTypeOfService": 0,
            "StudentWIOADetail.Youth": one_stop(self.youth_one_stop),
            "StudentWIOADetail.YouthDateofLastService": "",
            "StudentWIOADetail.YouthProviderName": "",
            "StudentWIOADetail.YouthTypeOfService": 0,
            "StudentWIOADetail.VocationalRehabilitation": voc_rehab(self.voc_rehab),
            "StudentWIOADetail.WagnerPeyserAct": y_n_u(self.wagner_peyser),
            "StudentWIOADetail.SchoolStatusAtParticipation": school_status(self.school_status),
            "StudentWIOADetail.ReceivedTraining": "",
            "StudentWIOADetail.EligibleTrainingProvider": "",
            "StudentWIOADetail.TypeTrainingServices": "",
            "StudentWIOADetail.EligibleTrainingProviderStudy": "",
            "StudentWIOADetail.EligibleTrainingProviderCIP": "",
            "StudentWIOADetail.TypeTrainingService2": "",
            "StudentWIOADetail.TypeTrainingService3": "",
            "Disability_12": true_false(self.adhd),
            "Disability_13": true_false(self.autism),
            "Disability_9": true_false(self.deaf_blind),
            "Disability_3": true_false(self.deaf),
            "Disability_6": true_false(self.emotional_disturbance),
            "Disability_15": true_false(self.k12_iep),
            "Disability_2": true_false(self.hard_of_hearing),
            "Disability_1": true_false(self.intellectual_disability),
            "Disability_10": true_false(self.multiple_disabilities),
            "Disability_7": true_false(self.orthopedic_impairment),
            "Disability_8": true_false(self.other_health_impairment),
            "Disability_11": true_false(self.learning_disability),
            "Disability_4": true_false(self.speech_or_lang_impairment),
            "Disability_14": true_false(self.traumatic_brain_injury),
            "Disability_5": true_false(self.visual_impairment),
            "SpecLearningDisId": "11",
            "Dislearning_4": true_false(self.dyscalculia),
            "Dislearning_3": true_false(self.dysgraphia),
            "Dislearning_2": true_false(self.dyslexia),
            "Dislearning_1": true_false(self.neurological_impairments),
            "HighestId": self.highest_level_completed,
            "HighLocId": self.school_location,
            "GoalId": "",
            "ReferralDate": "",
            "ReferralTo": "",
            "CommentDate": "",
            "Comment": "",
            "btnSave": "Create"
        }

        session.post(
            'https://workreadyu.lctcs.edu/Student/CreateWithWIOA/CreateLink',
            data=student
        )

        search = {
            'LastNameTextBox': self.student.last_name,
            'FirstNameTextBox': self.student.first_name,
            'FromTextBox': self.student.intake_date,
            'ToTextBox': self.student.intake_date,
            'btnFilter': 'Filter List'
        }

        wru = wru_search(session, search)
        try:
            wru = wru.decode('ascii')
        except AttributeError:
            pass

        self.student.WRU_ID = wru
        self.student.save()
        self.student.testify()
        self.student.track()

    def send(self, session):
        self.check_for_state_id(session)
        if self.student.WRU_ID == 'No ID':
            self.send_to_state(session)


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
        models.PROTECT,
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