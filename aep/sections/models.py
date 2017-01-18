from datetime import date, datetime, timedelta as td
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
    HISPANIC_CHAMBER = 'HC'
    WEST_BANK_LIB = 'WL'
    JOB_1 = 'J1'
    SITE_CHOICES = (
        (CITY_PARK, 'City Park'),
        (MID_CITY, 'NOALC'),
        (WEST_BANK, 'West Bank'),
        (JEFFERSON_PARISH, 'Jefferson Parish'),
        (SIDNEY_COLLIER, 'Sidney Collier'),
        (HISPANIC_CHAMBER, 'HCC'),
        (WEST_BANK_LIB, 'West Bank Regional Library'),
        (JOB_1, 'Job 1')
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
        related_name='sections',
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
    room = models.CharField(
        max_length=20,
        blank=True
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

    def get_waiting(self):
        return self.students.filter(status='W').order_by('created')

    def get_withdrawn(self):
        return self.students.filter(status='R')

    def begin(self):
        for student in self.get_active():
            student.activate()
            student.save()

    # Drops active students with 2 absences and fills their spots with waitlisted students in enrollment order
    def waitlist_update(self):
        for student in self.get_active():
            student.waitlist_drop()
        for student in self.get_waiting():
            student.add_from_waitlist()

    def enforce_attendance(self):
        for student in self.get_active():
            student.attendance_drop()

    def open_seats(self):
        if self.seats:
            return self.seats - self.students.filter(status='A').count()
        return None

    def is_full(self):
        return self.open_seats() < 1

    def over_full(self):
        return self.students.filter(status='W').count() > 4

    def get_days(self):
        days = []
        day_map = [
            ('monday', 'M', 0),
            ('tuesday', 'T', 1),
            ('wednesday', 'W', 2),
            ('thursday', 'R', 3),
            ('friday', 'F', 4),
            ('saturday', 'Sa', 5),
            ('sunday', 'Su', 6)
        ]
        for day in day_map:
            field = self._meta.get_field(day[0])
            if getattr(self, field.name):
                days.append(day)
        return days

    def get_days_str(self):
        days = self.get_days()
        days_str = []
        for day in days:
            field = self._meta.get_field(day[0])
            if getattr(self, field.name):
                days_str.append(day[1])
        return "".join(days_str)

    def get_class_dates(self):
        weekdays = [i[2] for i in self.get_days()]
        start, end = self.semester.start_date, self.semester.end_date
        class_dates = []
        date_range = end - start
        for j in range(date_range.days + 1):
            d = start + td(days=j)
            if d.weekday() in weekdays:
                class_dates.append(d)
        return class_dates

    def __str__(self):
        s = str(self.site)
        n = str(self.title)
        t = str(self.teacher)
        d = self.get_days_str()
        b = self.start_time.strftime('%I:%M%p')
        items = [s, n, t, d, b]
        return "|".join(items)

    def get_absolute_url(self):
        return reverse('sections:class detail', kwargs={'slug': self.slug})


class Enrollment(models.Model):

    ACTIVE = 'A'
    WAITING = 'W'
    WITHDRAWN = 'R'
    DROPPED = 'D'
    COMPLETED = 'C'
    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (WAITING, 'Waitlist'),
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

    class Meta:
        unique_together = ('student', 'section')

    def student_name(self):
        name = self.student.__str__()
        return name

    def class_name(self):
        name = self.section.title
        return name

    def times_attended(self):
        return self.attendance.filter(attendance_type='P').count()

    def times_absent(self):
        return self.attendance.filter(attendance_type='A').count()

    def get_attendance(self):
        return self.attendance.order_by(attendance__attendance_date)

    # Creates related attendance objects for student enrollment with correct dates and pending status
    def activate(self):
        if self.attendance.all().count() == 0:
            dates = self.section.get_class_dates()
            for day in dates:
                a = Attendance.objects.create(
                    enrollment=self,
                    attendance_date=day,
                    time_in=self.section.start_time,
                    time_out=self.section.end_time
                )
                a.save()

    # Drops students who have missed first two class periods
    def waitlist_drop(self):
        absent = self.times_absent()
        present = self.times_attended()
        if absent > 1 and present < 1:
            self.status = "D"
            self.save()

    # Adds students to active roster if class space exists
    def add_from_waitlist(self):
        if not self.section.is_full():
            self.status = 'A'
            self.save()

    # Check attendance for attendance policy compliance - change enrollment status if needed
    def attendance_drop(self):
        absences = self.times_absent()
        if absences > 4:
            self.status = 'D'
            self.save()

    def get_absolute_url(self):
        return reverse('sections:enrollment detail', kwargs={'pk': self.pk})

    def __str__(self):
        name = self.student_name()
        section = self.class_name()
        return name + ": enrolled in " + section


class Attendance(models.Model):

    PRESENT = 'P'
    ABSENT = 'A'
    PENDING = 'X'
    CANCELLED = 'C'
    TYPE_CHOICES = (
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
        (PENDING, 'Pending'),
        (CANCELLED, 'Cancelled'),
    )
    enrollment = models.ForeignKey(
        Enrollment,
        related_name='attendance'
    )
    attendance_type = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES,
        default='X'
    )
    attendance_date = models.DateField()
    time_in = models.TimeField(
        blank=True
    )
    time_out = models.TimeField(
        blank=True
    )

    class Meta:
        ordering = ['attendance_date', ]

    def hours(self):
        if self.attendance_type == 'P':
            d1 = datetime.combine(self.attendance_date, self.time_in)
            d2 = datetime.combine(self.attendance_date, self.time_out)
            delta = d2 - d1
            hours = delta.total_seconds() / 3600
            return float("{0:.2f}".format(hours))
        return 0

    def get_absolute_url(self):
        return reverse(
            'sections:single attendance',
            kwargs={
                'slug': self.enrollment.section.slug,
                'pk': self.pk
            }
        )
