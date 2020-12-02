from apiclient import discovery
from datetime import date, datetime, timedelta as td
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.errors import HttpError
from django.apps import apps
from django.db import models, IntegrityError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from core.utils import make_slug
from core.tasks import send_mail_task
from academics.models import Course
from people.models import Staff, Student
from people.tasks import pop_update_task
from semesters.models import Semester
from .tasks import activate_task, end_task, drop_task, enrollment_notification_task


class Site(models.Model):
    
    code = models.CharField(max_length=2)

    name = models.CharField(max_length=50)

    street_address = models.CharField(
        max_length=60,
        verbose_name="Street Address",
    )
    city = models.CharField(
        max_length=30,
    )
    state = models.CharField(
        max_length=2,
        default="LA"
    )
    zip_code = models.CharField(
        max_length=10,
    )

    def __str__(self):
        return(self.name)

class Section(models.Model):

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
        models.PROTECT,
        related_name='sections',
        null=True,
        blank=True
    )
    teacher = models.ForeignKey(
        Staff,
        models.PROTECT,
        related_name='classes',
        null=True,
        blank=True
    )
    course = models.ForeignKey(
        Course,
        models.PROTECT,
        related_name='sections',
        null=True,
        blank=True
    )
    g_suite_id = models.CharField(
        max_length=20,
        blank=True
    )

    site = models.ForeignKey(
        Site,
        models.PROTECT,
        related_name='sections',
        null=True,
        blank=True
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
    starting = models.DateField(null=True, blank=True)
    ending = models.DateField(null=True, blank=True)
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
        s = str(self.site.code)
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

    def get_completed(self):
        return self.students.filter(status='C')

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

    @property
    def is_full(self):
        try:
            return self.open_seats() < 1
        except TypeError:
            return True


    @property
    def over_full(self):
        return self.get_waiting().count() > 4

    @property
    def start_date(self):
        if self.starting is not None:
            return self.starting
        else:
            return self.semester.start_date

    @property
    def end_date(self):
        if self.ending is not None:
            return self.ending
        else:
            return self.semester.end_date

    def begin(self):
        for student in self.get_active():
            activate_task.delay(enrollment_id=student.id)

    def end(self):
        for student in self.get_active():
            end_task.delay(enrollment_id=student.id)

    def roster_to_classroom(self):

        scopes = [
            'https://www.googleapis.com/auth/classroom.rosters',
            'https://www.googleapis.com/auth/classroom.profile.emails'
        ]
        credentials = ServiceAccountCredentials._from_parsed_json_keyfile(
            keyfile_dict=settings.KEYFILE_DICT,
            scopes=scopes
        )
        shane = credentials.create_delegated('shane.dicks@elearnclass.org')
        http_auth = shane.authorize(Http())
        service = discovery.build('classroom', 'v1', http=http_auth)

        roster = service.courses().students().list(
            courseId=self.g_suite_id,
        ).execute()
        print("Roster page found with {} students".format(len(roster['students'])))
        rostered_emails = [
            x['profile'].get('emailAddress')
            for x
            in roster['students']
            if x['profile'].get('emailAddress')
        ]
        print("{} emails added to rostered emails".format(len(rostered_emails)))
        token = roster.get('nextPageToken')
        print("Token {}".format(token))
        while token is not None:
            roster = service.courses().students().list(
                courseId=self.g_suite_id,
                pageToken=token
            ).execute()
            print("Roster page found with {} students".format(len(roster['students'])))
            current_emails = [
                x['profile'].get('emailAddress')
                for x
                in roster['students']
                if x['profile'].get('emailAddress')
            ]
            rostered_emails.extend(current_emails)
            print("{} emails added to rostered emails".format(len(current_emails)))
            token = roster.get('nextPageToken')
            print("Token {}".format(token))
        print("Rostered email list: {}".format(rostered_emails))

        students = self.students.filter(status='A')
        Elearn = apps.get_model('coaching', 'ElearnRecord')
        new_emails = [
            elearn.g_suite_email
            for elearn
            in Elearn.objects.filter(
                student__classes__in=students
            )
            if elearn.g_suite_email not in rostered_emails
        ]
        print("{} new emails found".format(len(new_emails)))

        def callback(request_id, response, exception):
            if exception is not None:
                print("Error adding {0} to course: {1}".format(
                    request_id,
                    exception
                ))
            else:
                print("User {0} added successfully".format(
                    response.get('profile').get('emailAddress')))

        batch = service.new_batch_http_request(callback=callback)

        for email in new_emails:
            s = {
                "userId": email
            }
            request = service.courses().students().create(
                courseId=self.g_suite_id,
                body=s
            )
            batch.add(request, request_id=email)
        batch.execute()

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
                            att_hours=sub.get('assignedGrade', 0),
                            online=True,
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
                send_mail_task.delay(
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
            drop_task.delay(enrollment_id=student.id)

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
                send_mail_task.delay(
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
        if self.starting is not None:
            start = self.starting
        else:
            start = self.semester.start_date
        if self.ending is not None:
            end = self.ending
        else:
            end = self.semester.end_date
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
        models.CASCADE,
        related_name='classes'
    )
    section = models.ForeignKey(
        Section,
        models.PROTECT,
        related_name='students'
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.PROTECT,
        related_name='enrollment_records'
    )
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='A'
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.PROTECT,
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
        total = 0
        for att in self.attendance.filter(attendance_type='P'):
            total += att.hours
        return total

    # Creates related attendance objects for student enrollment with correct dates and pending status
    def activate(self):
        if self.attendance.all().count() == 0:
            dates = self.section.get_class_dates()
            online = self.section.program == 'ELRN' or self.section.site.code == 'OL'
            for day in dates:
                a = Attendance.objects.create(
                    enrollment=self,
                    attendance_date=day,
                    time_in=self.section.start_time,
                    time_out=self.section.end_time,
                    online=online
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
                send_mail_task.delay(
                    subject="We're sorry {student}, but you've been dropped from {section}".format(
                        student=self.student.first_name,
                        section=self.section.title),
                    message="According to our attendance policy, "
                    "students who miss the first two class periods "
                    "are dropped to make room for waitlisted students.\n"
                    "Please stop by our main office or call "
                    "504-671-5434 for more information.",
                    from_email="attendance_robot@dccaep.org",
                    recipient_list=[self.student.email],
                )
            return True
        return False

    # Adds students to active roster if class space exists
    def add_from_waitlist(self):
        if not self.section.is_full:
            self.status = 'A'
            self.save()
            if self.student.email:
                send_mail_task.delay(
                    subject="Good News! You've been added to {section}".format(
                        section=self.section.title
                    ),
                    message="Hi {student} \n"
                    "Space has opened up in {section} and you have been added the roster.\n"
                    "To keep your spot, please attend this class the next time it meets.\n"
                    "If you are unsure when that is, "
                    "stop by our main office or call 504-671-5434".format(
                        student=self.student.first_name,
                        section=self.section.title),
                    from_email="class_roster_robot@dccaep.org",
                    recipient_list=[self.student.email],
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
                send_mail_task.delay(
                    subject="We're sorry {student}, but you've been dropped from {section}".format(
                        student=self.student.first_name,
                        section=self.section.title),
                    message="According to our program's attendance policy, "
                    "students who miss a class more than 4 times "
                    "will be dropped from that class. "
                    "You're still part of our program, you're just dropped from this class.\n"
                    "Please stop by our main office or call "
                    "504-671-5434 for more information.",
                    from_email="attendance_robot@dccaep.org",
                    recipient_list=[self.student.email]
                )

    def welcome_email(self):
        try:
            g_suite_email = self.student.elearn_record.g_suite_email
        except ObjectDoesNotExist:
            g_suite_email = ''
        if g_suite_email != '':
            recipients = [self.student.email, g_suite_email]
        else:
            recipients = [self.student.email]
        if self.student.email:
            send_mail_task.delay(
                subject="Delgado Adult Education - Welcome to the new session! ¡Bienvenido a la nueva sesión!",
                message="",
                html_message="<p>Dear Students,</p><p>We are excited to have you back "
                "online with us for another session. If you’re joining us for the first "
                "time, welcome!</p><p>As an update, classes are live now. You can login "
                "to <a href='http://classroom.google.com'>Google Classroom</a> to get "
                "started with your new classes.</p><p><strong>How to login</strong><br>"
                "You can use your school account to login to Google Classroom: "
                "<strong>{g_suite_email}</strong></p><p><strong>Questions?</strong><br>"
                "If you have any questions, including how to reset your password, "
                "please reach out to your teachers or coach. You can also email our help "
                "desk anytime at <a href='mailto:coach@elearnclass.org'>coach@elearnclass.org"
                "</a></p><p>We look forward to working with you this session</p><p>"
                "Be safe and stay healthy!</p><p>All the very best,<br>Delgado Adult "
                "Education Program</p><hr>"
                "<p>Queridos estudiantes,</p><p>Estamos emocionados de tenerles nuevamente en"
                " línea con nosotros para otra sesión. Si te unes a nosotros por la primera "
                "vez, ¡Bienvenido!</p><p>Las clases están en vivo ahora. Puede iniciar su sesión en "
                "<a href='http://classroom.google.com'>Google Classroom</a> para comenzar con sus "
                "nuevas clases.</p><p><strong>Cómo iniciar sesión</strong><br>"
                "Puede usar su cuenta del colegio para iniciar sesión en Google Classroom: "
                "<strong>{g_suite_email}</strong></p><p><strong>Preguntas?</strong><br>"
                "Si tiene alguna pregunta, incluido cómo restablecer su contraseña, comuníquese "
                "con sus maestros o entrenador. También puede enviar un correo electrónico a "
                "nuestro servicio de asistencia en cualquier momento a "
                "<a href='mailto:coach@elearnclass.org'>coach@elearnclass.org"
                "</a></p><p>Esperamos con interés trabajar con usted en esta sesión.</p><p>"
                "¡Esté seguro y manténgase saludable!</p><p>Todo lo mejor,<br>Programa de "
                "educación para adultos Delgado</p>".format(g_suite_email=g_suite_email),
                from_email="welcome@dccaep.org",
                recipient_list=recipients,
            )

    def save(self, *args, **kwargs):
        super(Enrollment, self).save(*args, **kwargs)
        mod = self.last_modified.date()
        if self.section.starting is not None:
            start = self.section.starting
        else:
            start = self.section.semester.start_date
        if self.section.ending is not None:
            end = self.section.ending
        else:
            end = self.section.semester.end_date
        if mod > start and mod < end and self.status is not self.COMPLETED:
            enrollment_notification_task.delay(self.id)


class Attendance(models.Model):

    PRESENT = 'P'
    ABSENT = 'A'
    PENDING = 'X'
    CANCELLED = 'C'
    TYPE_CHOICES = (
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
        (PENDING, '-----'),
        (CANCELLED, 'Cancelled'),
    )
    enrollment = models.ForeignKey(
        Enrollment,
        models.CASCADE,
        related_name='attendance'
    )
    attendance_type = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES,
        default='X'
    )
    attendance_date = models.DateField()
    time_in = models.TimeField(
        blank=True,
        null=True
    )
    time_out = models.TimeField(
        blank=True,
        null=True
    )
    att_hours = models.FloatField(
        blank=True,
        null=True
    )
    online = models.BooleanField(
        default=False)
    notes = models.CharField(
        max_length=80,
        blank=True,       
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

    @property
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

    @property
    def enrolled_hours(self):
        d1 = datetime.combine(self.attendance_date, self.time_in)
        d2 = datetime.combine(self.attendance_date, self.time_out)
        delta = d2 - d1
        hours = delta.total_seconds() / 3600
        return float("{0:.2f}".format(hours))

    def save(self, *args, **kwargs):
        super(Attendance, self).save(*args, **kwargs)
        if self.attendance_type == 'P':
            pop_update_task.delay(self.enrollment.student.id, self.attendance_date)
