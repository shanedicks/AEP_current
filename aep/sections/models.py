from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from core.utils import make_slug


class Semester(models.Model):

    title = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()


class Section(models.Model):

    title = models.CharField(max_length=50)
    semester = models.ForeignKey(
        Semester,
        null=True,
        blank=True
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='teacher_classes',
        null=True,
        blank=True
    )
    seats = models.IntegerField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    WRU_ID = models.IntegerField(null=True, blank=True)
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    slug = models.CharField(unique=True, max_length=5, default=make_slug)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('sections:class detail', kwargs={'slug': self.slug})


class Enrollment(models.Model):

    ACTIVE = 'A'
    WITHDRAWN = 'W'
    DROPPED = 'D'
    COMPLETED = 'C'
    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (WITHDRAWN, 'Withdrawn'),
        (DROPPED, 'Dropped'),
        (COMPLETED, 'Completed'),
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='student_classes'
    )
    section = models.ForeignKey(
        Section,
        related_name='students'
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='enrollment_records'
    )
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='A'
    )
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)


class Attendance(models.Model):

    PRESENT = 'P'
    ABSENT = 'A'
    CANCELLED = 'C'
    TYPE_CHOICES = (
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
        (CANCELLED, 'Cancelled'),
    )
    enrollment = models.ForeignKey(
        Enrollment,
        related_name='attendance'
    )
    attendance_type = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES
    )
    attendance_date = models.DateField()
    time_in = models.TimeField()
    time_out = models.TimeField()
