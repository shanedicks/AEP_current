from apiclient import discovery
from datetime import date, datetime, timedelta as td
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from django.db import models, IntegrityError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from core.utils import make_slug
from academics.models import Course
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
    CHARITY = 'CH'
    ONLINE = 'OL'
    SITE_CHOICES = (
        (CITY_PARK, 'City Park'),
        (MID_CITY, 'NOALC'),
        (WEST_BANK, 'West Bank'),
        (JEFFERSON_PARISH, 'Jefferson Parish'),
        (SIDNEY_COLLIER, 'Sidney Collier'),
        (HISPANIC_CHAMBER, 'HCC'),
        (WEST_BANK_LIB, 'West Bank Regional Library'),
        (JOB_1, 'Job 1'),
        (CHARITY, 'Charity'),
        (ONLINE, 'Online Classes')
    )
    ESL = 'ESL'
    CCR = 'CCR'
    TRANS = 'TRANS'
    ADMIN = 'ADMIN'
    ELEARN = 'ELRN'
    PROGRAM_CHOICES = (
        (ESL, 'ESL'),
        (CCR, 'CCR'),
        (ADMIN, 'Admin'),
        (ELEARN, 'eLearn'),
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
    course = models.ForeignKey(
        Course,
        related_name='sections',
        null=True,
        blank=True
    )
    g_suite_id = models.CharField(
        max_length=20,
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
    start_time = models.TimeField()
    end_time = models.TimeField()
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
        s = str(self.site)
        n = str(self.title)
        t = str(self.teacher)
        d = self.get_days_str()
        b = self.start_time.strftime('%I:%M%p')
        items = [s, n, t, d, b]
        return "|".join(items)

    def get_absolute_url(self):
        return reverse('sections:class detail', kwargs={'slug': self.slug})

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

    def open_seats(self):
        a = self.get_active().count()
        w = self.get_waiting().count()
        students = a + w
        if self.seats:
            return self.seats - students
        return None

    def is_full(self):
        return self.open_seats() < 1

    def over_full(self):
        return self.get_waiting().count() > 4

    def begin(self):
        for student in self.get_active():
            student.activate()
            student.save()

    def end(self):
        for student in self.get_active():
            if student.status == student.ACTIVE:
                student.status = student.COMPLETED
                student.save()

    def g_suite_attendance(self):
        scopes = ['https://www.googleapis.com/auth/classroom.coursework.students']

        credentials = ServiceAccountCredentials._from_parsed_json_keyfile(
            keyfile_dict=settings.KEYFILE_DICT,
            scopes=scopes
        )

        shane = credentials.create_delegated('shane.dicks@elearnclass.org')
        http_auth = shane.authorize(Http())
        service = discovery.build('classroom', 'v1', http=http_auth)
        raw = {}
        print("Starting", self.title)
        for student in self.get_all_students():
            try:
                if student.student.elearn_record.g_suite_email:
                    print("Fetching", student.student)
                    raw[student] = service.courses(
                    ).courseWork().studentSubmissions().list(
                        courseId=self.g_suite_id,
                        states='RETURNED',
                        courseWorkId='-',
                        userId=student.student.elearn_record.g_suite_email
                    ).execute()
                    print(
                        "Fetched",
                        len(raw[student].get('studentSubmissions', [])),
                        "records"
                    )
            except ObjectDoesNotExist:
                print(student.student, "has no elearn record. Skipping...")
        for key, value in raw.items():
            subs = value.get('studentSubmissions')
            if subs is not None:
                print('Creating attendance for', key.student)
                for sub in subs:
                    try:
                        a = Attendance.objects.create(
                            enrollment=key,
                            attendance_date=datetime.strptime(
                                sub['creationTime'].split('T')[0],
                                "%Y-%m-%d"
                            ).date(),
                            time_in=key.section.start_time,
                            time_out=key.section.start_time,
                            attendance_type='P',
                            att_hours=sub.get('assignedGrade', 0)
                        )
                        print(a)
                    except IntegrityError:
                        print("Duplicate attendance found. Skipping....")
        print("Finished with", self.title)

    # Drops active students with 2 absences and fills their spots with waitlisted students in enrollment order
    def waitlist_update(self):
        dropped = []
        added = []
        for student in self.get_active():
            if student.waitlist_drop():
                dropped.append(str(student.student))
        for student in self.get_waiting():
            if student.add_from_waitlist():
                added.append(str(student.student))
        self.begin()
        if len(dropped) > 0:
            if self.teacher.email:
                send_mail(
                    "Delgado Adult Ed Dropped Student Notice {day}".format(day=datetime.today().date()),
                    "Hi {teacher},\n"
                    "In accordance with our attendance policy, "
                    "we have dropped the following students from {section}:\n"
                    "{drop}\n"
                    "We have also added the following waitlisted "
                    "students to your active roster:\n"
                    "{add}\n"
                    "All these students listed have been notified "
                    "by email that their status has changed.\n"
                    "Please understand that waitlisted students "
                    "are not excused for days missed while on the waitlist. "
                    "Consider calling these newly added students to be sure "
                    "they are aware of the change. Thanks".format(
                        section=self.title,
                        teacher=self.teacher.first_name,
                        drop=dropped,
                        add=added),
                    "admin@dccaep.org",
                    [self.teacher.email],
                    fail_silently=False
                )

    def enforce_attendance(self):
        for student in self.get_active():
            student.attendance_drop()

    def attendance_reminder(self):
        if self.teacher.email:
            today = datetime.today()
            last_week = datetime.today() - td(days=7)
            att = Attendance.objects.filter(
                attendance_date__lt=today,
                attendance_date__gte=last_week,
                attendance_type='X',
                enrollment__section=self,
                enrollment__status='A'
            ).count()
            if att > 1:
                send_mail(
                    "Delgado Adult Ed Attendance Reminder {day}".format(day=datetime.today().date()),
                    "Hi {teacher} \n"
                    "\n"
                    "Your attendance for {section} is incomplete.\n"
                    "By updating your attendance in a timely way, "
                    "we are able to ensure that students comply "
                    "with program attendance and testing policies.\n\n"
                    "Please update or check your attendance for accuracy as soon as possible.".format(
                        section=self.title,
                        teacher=self.teacher.first_name
                    ),
                    "admin@dccaep.org",
                    [self.teacher.email],
                    fail_silently=False
                )

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

    def __str__(self):
        name = self.student_name()
        section = self.class_name()
        return name + ": enrolled in " + section

    def get_absolute_url(self):
        return reverse('sections:enrollment detail', kwargs={'pk': self.pk})

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
        return self.attendance.order_by('attendance_date')

    def total_hours(self):
        hours = 0
        for att in self.attendance.filter(attendance_type='P'):
            hours += att.hours()
        return hours

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
            if self.student.email:
                send_mail(
                    "We're sorry {student}, but you've been dropped from {section}".format(
                        student=self.student.first_name,
                        section=self.section.title),
                    "According to our attendance policy, "
                    "students who miss the first two class periods "
                    "are dropped to make room for waitlisted students.\n"
                    "Please stop by our main office or call "
                    "504-671-5434 for more information.",
                    "attendance_robot@dccaep.org",
                    [self.student.email],
                    fail_silently=False)
            return True
        return False

    # Adds students to active roster if class space exists
    def add_from_waitlist(self):
        if not self.section.is_full():
            self.status = 'A'
            self.save()
            if self.student.email:
                send_mail(
                    "Good News! You've been added to {section}".format(
                        section=self.section.title
                    ),
                    "Hi {student} \n"
                    "Space has opened up in {section} and you have been added the roster.\n"
                    "To keep your spot, please attend this class the next time it meets.\n"
                    "If you are unsure when that is, "
                    "stop by our main office or call 504-671-5434".format(
                        student=self.student.first_name,
                        section=self.section.title),
                    "class_roster_robot@dccaep.org",
                    [self.student.email],
                    fail_silently=False
                )
            return True
        return False

    # Check attendance for attendance policy compliance - change enrollment status if needed
    def attendance_drop(self):
        absences = self.times_absent()
        policy = self.section.semester.allowed_absences
        if absences > policy:
            self.status = 'D'
            self.save()
            if self.student.email:
                send_mail(
                    "We're sorry {student}, but you've been dropped from {section}".format(
                        student=self.student.first_name,
                        section=self.section.title),
                    "According to our program's attendance policy, "
                    "students who miss a class more than 4 times "
                    "will be dropped from that class. "
                    "You're still part of our program, you're just dropped from this class.\n"
                    "Please stop by our main office or call "
                    "504-671-5434 for more information.",
                    "attendance_robot@dccaep.org",
                    [self.student.email],
                    fail_silently=False)


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
    att_hours = models.IntegerField(
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['attendance_date', ]
        unique_together = ('enrollment', 'attendance_date', 'att_hours')

    def __str__(self):
        s = str(self.enrollment.student)
        d = self.attendance_date.strftime('%Y-%m-%d')
        t = self.get_attendance_type_display()
        return " | ".join([d, s, t])

    def get_absolute_url(self):
        return reverse(
            'sections:single attendance',
            kwargs={
                'slug': self.enrollment.section.slug,
                'pk': self.pk
            }
        )

    def hours(self):
        if self.att_hours:
            return self.att_hours
        else:
            if self.attendance_type == 'P':
                d1 = datetime.combine(self.attendance_date, self.time_in)
                d2 = datetime.combine(self.attendance_date, self.time_out)
                delta = d2 - d1
                hours = delta.total_seconds() / 3600
                return float("{0:.2f}".format(hours))
            return 0
