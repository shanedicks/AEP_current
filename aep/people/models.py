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

    student = models.OneToOneField(
        Student,
        models.CASCADE,
        related_name='WIOA'
    )
