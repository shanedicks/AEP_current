from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string


def make_AEP_ID():
    return get_random_string(length=8, allowed_chars='0123456789')


def make_slug():
    return get_random_string(length=5)


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

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"))

    intake_date = models.DateField(null=True, blank=True)
    WRU_ID = models.IntegerField(null=True, blank=True)
    AEP_ID = models.IntegerField(unique=True, default=make_AEP_ID)


class Staff(Profile):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("user"))

    bio = models.TextField(blank=True, max_length=4000)
