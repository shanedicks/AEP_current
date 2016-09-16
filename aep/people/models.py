from datetime import date
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from core.utils import make_slug, make_AEP_ID


class Profile(models.Model):

    phone = models.CharField(max_length=20, blank=True)
    alt_phone = models.CharField(max_length=20, blank=True)
    street_address_1 = models.CharField(max_length=60, blank=True)
    street_address_2 = models.CharField(max_length=60, blank=True)
    city = models.CharField(max_length=30, blank=True)
    state = models.CharField(max_length=2, blank=True)
    dob = models.DateField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=60, blank=True)
    ec_phone = models.CharField(max_length=20, blank=True)
    ec_email = models.EmailField(max_length=40, blank=True)
    slug = models.CharField(unique=True, default=make_slug, max_length=5)

    class Meta:
        abstract = True

    def __str__(self):
        return self.user.get_full_name()


class Student(Profile):

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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='student',
        verbose_name=_("user"))

    intake_date = models.DateField(null=True, blank=True, default=date.today)
    WRU_ID = models.IntegerField(null=True, blank=True)
    AEP_ID = models.IntegerField(unique=True, default=make_AEP_ID)
    US_citizen = models.BooleanField(default=False)
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default='F')

    marital_status = models.CharField(
        max_length=1,
        choices=MARITAL_STATUS_CHOICES,
        default='S')

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
