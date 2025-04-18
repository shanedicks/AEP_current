import logging
from apiclient import discovery
from datetime import date, datetime, timedelta as td
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.errors import HttpError
from django.apps import apps
from django.db import models, IntegrityError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils import timezone
from core.utils import make_slug
from core.tasks import send_mail_task
from academics.models import Course
from people.models import Staff, Student
from people.tasks import pop_update_task
from semesters.models import Semester
from core.tasks import send_sms_task
from .tasks import (activate_task, end_task, drop_task,
    enrollment_notification_task, cancel_class_task)

logger = logging.getLogger(__name__)

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

    ESL = 'ELL'
    CCR = 'CCR'
    TRANS = 'TRANS'
    ADMIN = 'ADMIN'
    ELEARN = 'ELRN'
    PROGRAM_CHOICES = (
        (ESL, 'ELL'),
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

    g_suite_link = models.CharField(
        max_length=100,
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
    closed = models.BooleanField(
        default=False
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

    att_summary = models.BooleanField(default = False)
    att_table = models.BooleanField(default = True)
    import_essential_ed = models.BooleanField(default = False)
    import_duolingo = models.BooleanField(default = False)

    def __str__(self):
        s = str(self.site.code)
        n = str(self.title)
        t = str(self.teacher)
        d = self.get_days_str()
        b = self.start_time.strftime('%I:%M%p')
        try:
            sem = "({0})".format(str(self.semester.id))
        except ObjectDoesNotExist:
            sem = ''
        items = [s, n, t, d, b, sem]
        return "|".join(items)

    def get_absolute_url(self):
        return reverse('sections:class detail', kwargs={'slug': self.slug})

    def get_all_students(self):
        return self.students.all()

    def get_students(self):
        return self.students.exclude(status='D')

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
        if self.seats:
            return self.get_active().count() >= self.seats
        else:
            return True


    @property
    def over_full(self):
        return self.get_waiting().count() > 12

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
        shane = credentials.create_delegated('greenbean@elearnclass.org')
        http_auth = shane.authorize(Http())
        service = discovery.build('classroom', 'v1', http=http_auth)

        roster = service.courses().students().list(
            courseId=self.g_suite_id,
        ).execute()
        if 'students' in roster:
            rostered_emails = [
                x['profile'].get('emailAddress').lower()
                for x
                in roster['students']
                if x['profile'].get('emailAddress')
            ]
            token = roster.get('nextPageToken')
            while token is not None:
                roster = service.courses().students().list(
                    courseId=self.g_suite_id,
                    pageToken=token
                ).execute()
                current_emails = [
                    x['profile'].get('emailAddress')
                    for x
                    in roster['students']
                    if x['profile'].get('emailAddress')
                ]
                rostered_emails.extend(current_emails)
                token = roster.get('nextPageToken')
        else:
            rostered_emails = []
        logger.info("{1} roster: {0}".format(rostered_emails, self.title))

        Elearn = apps.get_model('coaching', 'ElearnRecord')

        active_students = self.students.filter(status='A')
        active_emails = [
            elearn.g_suite_email.lower()
            for elearn
            in Elearn.objects.filter(
                student__classes__in=active_students
            )
        ]
        logger.info("{1} active: {0}".format(active_emails, self.title))
        inactive_emails = [
            email
            for email
            in rostered_emails
            if email not in active_emails
        ]
        logger.info("{1} inactive: {0}".format(inactive_emails, self.title))
        new_emails = [
            email
            for email
            in active_emails
            if email not in rostered_emails
            and email != ''
        ]
        logger.info("{1} new: {0}".format(new_emails, self.title))
        def drop_callback(request_id, response, exception):
            if exception is not None:
                logger.error("Error removing {0} from course:{1}".format(
                    request_id,
                    exception
                ))
            else:
                logger.info("User {0} removed successfully".format(request_id))

        drop_batch = service.new_batch_http_request(callback=drop_callback)
        for email in inactive_emails:
            request = service.courses().students().delete(
                courseId=self.g_suite_id,
                userId=email
            )
            drop_batch.add(request, request_id=email)
        drop_batch.execute()

        def add_callback(request_id, response, exception):
            if exception is not None:
                logger.error("Error adding {0} to course: {1}".format(
                    request_id,
                    exception
                ))
            else:
                logger.info("User {0} added successfully".format(
                    response.get('profile').get('emailAddress')))

        batch_list = [
            new_emails[i:i + 50] 
            for i 
            in range(0, len(new_emails), 50)
        ]
        for email_batch in batch_list:
            batch = service.new_batch_http_request(callback=add_callback)
            for email in email_batch:
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

        shane = credentials.create_delegated('greenbean@elearnclass.org')
        http_auth = shane.authorize(Http())
        service = discovery.build('classroom', 'v1', http=http_auth)
        raw = {}
        logger.info("Starting", self.title)
        for student in self.get_all_students():
            try:
                if student.student.elearn_record.g_suite_email:
                    logger.info("Fetching", student.student)
                    raw[student] = service.courses(
                    ).courseWork().studentSubmissions().list(
                        courseId=self.g_suite_id,
                        states='RETURNED',
                        courseWorkId='-',
                        userId=student.student.elearn_record.g_suite_email
                    ).execute()
                    logger.info(
                        "Fetched",
                        len(raw[student].get('studentSubmissions', [])),
                        "records"
                    )
            except ObjectDoesNotExist:
                logger.warning(student.student, "has no elearn record. Skipping...")
        for key, value in raw.items():
            subs = value.get('studentSubmissions')
            if subs is not None:
                logger.info('Creating attendance for', key.student)
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
                        logger.info(a)
                    except IntegrityError:
                        logger.warning("Duplicate attendance found. Skipping....")
        logger.info("Finished with", self.title)

    def get_g_suite_link(self):
        scopes = ['https://www.googleapis.com/auth/classroom.courses']

        credentials = ServiceAccountCredentials._from_parsed_json_keyfile(
            keyfile_dict=settings.KEYFILE_DICT,
            scopes=scopes
        )

        shane = credentials.create_delegated('greenbean@elearnclass.org')
        http_auth = shane.authorize(Http())
        service = discovery.build('classroom', 'v1', http=http_auth)


        course = service.courses().get(id=self.g_suite_id).execute()
        self.g_suite_link = course.get('alternateLink')
        self.save()

    # Drops active students with 2 absences and fills their spots with waitlisted students in enrollment order
    def waitlist_update(self):
        logger.info(f"Updating waitlist for {self.__str__()}")
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
                    "Delgado Adult Ed Dropped Student Notice | {section} - {day}".format(section=self.title, day=timezone.now().date()),
                    "Hi {teacher},\n"
                    "In accordance with our attendance policy, "
                    "we have dropped the following students from {section}:\n"
                    "{drop}\n"
                    "We have also added the following waitlisted "
                    "students to your active roster:\n"
                    "{add}\n"
                    "All these students listed have been notified "
                    "by email that their status has changed.\n"
                    "Consider calling these newly added students to be sure "
                    "they are aware of the change. Thanks".format(
                        section=self.title,
                        teacher=self.teacher.first_name,
                        drop=dropped,
                        add=added),
                    "admin@dccaep.org",
                    [self.teacher.email, "adulted@dcc.edu"],
                )

    def enforce_attendance(self):
        logger.info(f"Enforcing attendance for {self.__str__()}")
        dropped = []
        for student in self.get_active():
            if student.attendance_drop():
                dropped.append(str(student.student))
        if len(dropped) > 0:
            if self.teacher.email:
                send_mail_task.delay(
                    "Delgado Adult Ed Dropped Student Notice | {section} - {day}".format(section=self.title, day=timezone.now().date()),
                    "Hi {teacher},\n"
                    "In accordance with our attendance policy, "
                    "we have dropped the following students from {section}:\n"
                    "{drop}\n"
                    "All these students listed have been notified "
                    "by email that their status has changed.\n"
                    "Consider calling these newly added students to be sure "
                    "they are aware of the change. Thanks".format(
                        section=self.title,
                        teacher=self.teacher.first_name,
                        drop=dropped
                    ),
                    "admin@dccaep.org",
                    [self.teacher.email, "adulted@dcc.edu"],
                )

    def attendance_reminder(self, send_mail=True):
        today = timezone.now()
        last_week = timezone.now() - td(days=7)
        att_count = Attendance.objects.filter(
            attendance_date__lt=today,
            attendance_date__gte=last_week,
            attendance_type='X',
            enrollment__section=self,
            enrollment__status='A'
        ).count()
        try:
            teacher = self.teacher
            email = teacher.email
        except ObjectDoesNotExist:
            email = ''
        sent = False
        if send_mail and att_count > 0 and email:
                send_mail_task.delay(
                    "Delgado Adult Ed Attendance Reminder {day}".format(day=timezone.now().date()),
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
                )
                sent = True
        return (att_count, sent)

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
    get_days_str.short_description = "Days"

    def get_days_names(self):
        days = [s[0].title() for s in self.get_days()]
        if len(days) > 1:
            out = ", ".join(days[:-1]) +" and "+days[-1]
        elif len(days) == 1:
            out = days[0]
        else:
            out = ""
        return out

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

    def get_daily_attendance_rate(self):
        days = len(self.get_class_dates())
        rates = []
        if self.students.all().count() > 0:
            att_matrix = [
                [att.attendance_type for att in student.attendance.all()]
                for student
                in self.students.all()
            ]
            days_range = min(days, max([len(row) for row in att_matrix]))
            daily_matrix = [
                [row[i] if len(row) > i else 'X' for row in att_matrix]
                for i
                in range(days)
            ]
            rates = [
                "{:.0%}".format(
                    round(len([att for att in row if att =='P']) / len(row), 2)
                )
                if len(row) > 0 else 0
                for row
                in daily_matrix
            ]
        return rates

    def copy_roster(self, new_section, user=None, student_list=None):
        User = get_user_model()

        if not user:
            user = self.teacher.user

        if not student_list:
            student_list = [
                student.student for student
                in self.students.exclude(
                    status__in=[Enrollment.DROPPED, Enrollment.WITHDRAWN]
                )
            ]

        for student in student_list:
            try:
                Enrollment.objects.create(
                    creator=user,
                    student=student,
                    section=new_section
                )
            except IntegrityError:
                pass


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
    schedule_sent = models.BooleanField(default=False)

    reported = models.BooleanField(default=False)

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

    def last_attended(self):
        return self.attendance.filter(attendance_type='P').latest('attendance_date').attendance_date

    def get_attendance(self):
        return self.attendance.order_by('attendance_date')

    def total_hours(self):
        hours = sum([att.hours for att in self.attendance.filter(attendance_type='P')]) 
        return round(hours, 2)

    def attendance_table_row(self):
        return [self.attendance.filter(attendance_date=date) for date in self.section.get_class_dates()]

    def get_skill_masteries(self):
        masteries = apps.get_model('academics', 'SkillMastery').objects.filter(
            student=self.student, 
            skill__in=self.section.course.skills.all()
        )
        return masteries

    # Creates related attendance objects for student enrollment with correct dates and pending status
    def activate(self):
        dates = self.section.get_class_dates()
        created_dates = self.attendance.dates('attendance_date', 'day')
        new_dates = [x for x in dates if x not in created_dates]
        online = self.section.program == 'ELRN' or self.section.site.code == 'OL'
        for day in new_dates:
            a = Attendance.objects.create(
                enrollment=self,
                attendance_date=day,
                time_in=self.section.start_time,
                time_out=self.section.end_time,
                online=online
            )
            if day < timezone.now().date():
                a.attendance_type = Attendance.CANCELLED
            a.save()
        if self.section.course is not None:
            sm = apps.get_model('academics', 'SkillMastery')
            for skill in self.section.course.skills.all():
                if sm.objects.filter(skill=skill, student=self.student).count() == 0:
                    sm.objects.create(
                        skill=skill,
                        student=self.student,
                        certifier=self.section.teacher,
                        cert_date=dates[0]
                    )

    # Drops students who have missed first two class periods
    def waitlist_drop(self):
        absent = self.times_absent()
        present = self.times_attended()
        if absent > 1 and present < 1:
            self.status = "D"
            self.save()
            logger.info(f"{self.student} dropped from {self.section}")
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
                    from_email="enrollment_robot@elearnclass.org",
                    recipient_list=[self.student.email],
                )
            return True
        return False

    # Adds students to active roster if class space exists
    def add_from_waitlist(self):
        if not self.section.is_full:
            logger.info(f"Adding {self.student} to {self.section.__str__()}")
            self.status = 'A'
            self.save()
            if self.student.email:
                send_mail_task.delay(
                    subject="Good News! You've been added to {section}".format(
                        section=self.section.title
                    ),
                    message="""Hi {student} \n"
                    The wait is over!  A seat is open in {teacher}'s {section}.
                    Please visit {site},  Room {room} on {days} at {start_time} to begin class.
                    If you have any questions, please call the office at 504-671-5434.
                    """.format(
                            student=self.student.first_name,
                            teacher=self.section.teacher.first_name,
                            site = self.section.site.name,
                            room = self.section.room,
                            days = self.section.get_days_names(),
                            start_time = self.section.start_time,
                            section=self.section.title
                        ),
                    from_email="enrollment_robot@elearnclass.org",
                    recipient_list=[self.student.email],
                )
            if self.student.phone:
                send_sms_task.delay(
                    self.student.phone,
                    "You have been added to a Delgado Adult Education class. Please check your email for your schedule"
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
                    message=f"According to our program's attendance policy, "
                    "students who miss a class more than {policy} times "
                    "will be dropped from that class. "
                    "You're still part of our program, you're just dropped from this class.\n"
                    "Please stop by our main office or call "
                    "504-671-5434 for more information.",
                    from_email="enrollment_robot@elearnclass.org",
                    recipient_list=[self.student.email]
                )
            return True
        else:
            return False

    def welcome_email(self):
        try:
            g_suite_email = self.student.elearn_record.g_suite_email
        except ObjectDoesNotExist:
            g_suite_email = ''
        emails = [g_suite_email, self.student.email]
        recipients = [email for email in emails if email != '']
        if len(recipients) > 0:
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
                from_email="enrollment_robot@elearnclass.org",
                recipient_list=recipients,
            )


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
        models.PROTECT,
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
        if self.att_hours is not None:
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
        d1 = datetime.combine(self.attendance_date, self.enrollment.section.start_time)
        d2 = datetime.combine(self.attendance_date, self.enrollment.section.end_time)
        delta = d2 - d1
        hours = delta.total_seconds() / 3600
        return float("{0:.2f}".format(hours))

    def save(self, *args, **kwargs):
        super(Attendance, self).save(*args, **kwargs)
        if self.attendance_type == 'P':
            pop_update_task.delay(self.enrollment.student.id, self.attendance_date)

class Message(models.Model):

    title = models.CharField(
        max_length=100
    )

    sections = models.ManyToManyField(
        Section,
    )

    message = models.CharField(
        max_length=160
    )

    sent = models.DateTimeField(
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def send_message(self):
        sections = self.sections.all()
        students = apps.get_model('people', 'Student').objects.filter(
            classes__section__in=sections
        ).distinct()
        for student in students:
            send_sms_task.delay(
                dst=student.phone,
                message=self.message
            )
        self.sent = timezone.now()
        self.save()

class Cancellation(models.Model):

    section = models.ForeignKey(
            Section,
            models.PROTECT,
            related_name = 'cancellations',
        )

    cancellation_date = models.DateField()

    cancelled_by = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            models.PROTECT,
            related_name = 'cancellations'
    )

    notification_sent = models.BooleanField(
        default=False
    )

    send_notification = models.BooleanField(
        default=False
    )

    def __str__(self):
        date = self.cancellation_date.strftime('%Y-%m-%d')
        return "|".join([date, self.section.__str__()])
