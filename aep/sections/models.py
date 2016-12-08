from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from core.utils import make_slug
from people.models import Staff, Student
from semesters.models import Semester


class Section(models.Model):

    CITY_PARK = 'CP'
    MID_CITY = 'MC'
    WEST_BANK = 'WB'
    JEFFERSON_PARISH = 'JP'
    SIDNEY_COLLIER = 'SC'
    SITE_CHOICES = (
        (CITY_PARK, 'City Park'),
        (MID_CITY, 'NOALC'),
        (WEST_BANK, 'West Bank'),
        (JEFFERSON_PARISH, 'Jefferson Parish'),
        (SIDNEY_COLLIER, 'Sidney Collier')
    )
    ESL = 'ESL'
    CCR = 'CCR'
    TRANS = 'TRANS'
    PROGRAM_CHOICES = (
        (ESL, 'ESL'),
        (CCR, 'CCR'),
        (TRANS, 'Transitions')
    )
    title = models.CharField(max_length=50)
    semester = models.ForeignKey(
        Semester,
        null=True,
        blank=True
    )
    teacher = models.ForeignKey(
        Staff,
        related_name='classes',
        null=True,
        blank=True
    )
    site = models.CharField(
        max_length=2,
        choices=SITE_CHOICES,
        blank=True,
    )
    program = models.CharField(
        max_length=5,
        choices=PROGRAM_CHOICES,
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

    def get_all_students(self):
        return self.students.all()

    def get_active(self):
        return self.students.filter(status='A')

    def get_dropped(self):
        return self.students.filter(status='D')

    def get_withdrawn(self):
        return self.students.filter(status='W')

    def open_seats(self):
        if self.seats:
            return self.seats - self.students.count()
        return None

    def is_full(self):
        return self.seats < self.students.count()

    def get_days_str(self):
        days = []
        day_map = [
            ('monday', 'M'),
            ('tuesday', 'T'),
            ('wednesday', 'W'),
            ('thursday', 'R'),
            ('friday', 'F'),
            ('saturday', 'Sa'),
            ('sunday', 'Su')
        ]
        for day in day_map:
            field = self._meta.get_field(day[0])
            if getattr(self, field.name):
                days.append(day[1])
        return "".join(days)

    def __str__(self):
        s = str(self.site)
        n = str(self.title)
        t = str(self.teacher)
        d = self.get_days_str()
        b = str(self.start_time)
        items = [s, n, t, d, b]
        return "-".join(items)

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
        Student,
        related_name='classes'
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
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='modified_enrollments',
        null=True
    )
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def student_name(self):
        name = self.student.__str__()
        return name

    def class_name(self):
        name = self.section.title
        return name

    def times_attended(self):
        pass

    def times_absent(self):
        pass

    # Check attendance for attendance policy compliance - change enrollment status if needed
    def enforce_attendance(self):
        pass

    def get_absolute_url(self):
        return reverse('sections:enrollment detail', kwargs={'pk': self.pk})

    def __str__(self):
        name = self.student_name()
        section = self.class_name()
        return name + ": enrolled in " + section

    class Meta:
        unique_together = ('student', 'section')


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
        choices=TYPE_CHOICES,
        default='C'
    )
    attendance_date = models.DateField()
    time_in = models.TimeField()
    time_out = models.TimeField()
