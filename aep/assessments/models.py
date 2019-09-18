from datetime import date, timedelta
from django.conf import settings
from core.tasks import send_mail_task
from django.urls import reverse
from django.db import models
from people.models import Staff, Student
from sections.models import Attendance, Site


class TestEvent(models.Model):

    TABE = 'TABE'
    CLAS_E = 'CLAS-E'
    TABE_LOC = 'TABE Locator'
    CLAS_E_LOC = 'CLAS-E Locator'
    ORIENTATION = 'Orientation'
    HISET_PRACTICE = 'HiSET Practice'
    EXIT_EXAM = 'Exit Exam'
    TEST_CHOICES = (
        (TABE, 'TABE Test'),
        (TABE_LOC, 'TABE Locator'),
        (CLAS_E, 'CLAS-E Test'),
        (CLAS_E_LOC, 'CLAS-E Locator'),
        (ORIENTATION, 'Orientation'),
        (HISET_PRACTICE, 'HiSET Practice'),
        (EXIT_EXAM, 'Exit Exam')
    )

    proctor = models.ForeignKey(
        Staff,
        models.PROTECT,
        related_name="Tests",
        blank=True,
        null=True
    )

    test = models.CharField(
        choices=TEST_CHOICES,
        max_length=20
    )

    title = models.CharField(
        max_length=60,
        blank=True
    )

    seats = models.PositiveSmallIntegerField()

    start = models.DateTimeField()

    site = models.ForeignKey(
        Site,
        models.PROTECT,
        related_name="events",
        blank=True,
        null=True
    )

    room = models.CharField(
        max_length=60,
        blank=True
    )

    end = models.DateTimeField()

    full = models.BooleanField(
        default=False
    )

    class Meta:
        verbose_name = "Test Event"
        verbose_name_plural = "Test Events"
        ordering = [
            '-start'
        ]

    def __str__(self):
        if self.title:
            return self.title
        else:
            start_date = self.start.date().strftime("%a, %b %d")
            start_time = self.start.time().strftime("%I:%M%p")
            title = [self.test, start_date, start_time]
            return " | ".join(title)

    def get_absolute_url(self):
        return reverse(
            'assessments:test event detail',
            kwargs={'pk': self.pk}
        )

    def open_seats(self):
        if self.seats:
            return self.seats - self.students.count()
        return 0

    def check_full(self):
        if self.open_seats() < 1:
            self.full = True
            self.save()
        else:
            self.full = False
            self.save()

    def orientation_reminder(self):
        for student in self.students.all():
            if student.student.email:
                send_mail_task.delay(
                    subject="Your Orientation Reminder for the Delgado "
                    "Community College Adult Education Program!",
                    message="",
                    html_message="<p>Hi {student},</p><p>You have selected "
                    "to attend Orientation on {date:{dfmt}} at {time:{tfmt}} "
                    "at the City Park Campus (615 City Park Ave,"
                    " New Orleans, LA 70119).</p> <p>Later on, you can "
                    "choose to attend classes at other locations -- but for "
                    "New Student events you will need to come to the City Park"
                    " location.</p> <p>Please come to Building "
                    "7, Room 170.<a href='http://www.dcc.edu/about/locations"
                    "/city-park/map-directions.aspx'>Click here</a>"
                    " for directions and <a href='http://www.dcc."
                    "edu/documents/about/city-park-campus-map.pdf'>click here</a>"
                    " for a map of the campus.</p>"
                    "<br>"
                    "<p><strong>Your attendance of this event is required"
                    " to move forward in the registration process</strong>"
                    ".</p> <p>If you have any questions or a problem with "
                    " your appointment please <a href=https://docs.google.com/"
                    "forms/d/e/1FAIpQLSefXcnufXkaqnS5OAyTnCREC7dFA6AbviiPCdZQyy2krMAW4g/viewform>"
                    "click here for assistance</a>.</p><p>Si tiene preguntas"
                    " o problemas con su cita, haga <a href=https://docs.google.com/"
                    "forms/d/e/1FAIpQLSefXcnufXkaqnS5OAyTnCREC7dFA6AbviiPCdZQyy2krMAW4g/"
                    "viewform>clic aquí para obtener ayuda</a></p>"
                    "<br><p>Thank you,</p>"
                    "<p>The Adult Education Program</p>"
                    "<p>Delgado Community College</p>".format(
                        student=student.student.first_name,
                        dfmt='%m-%d-%Y',
                        tfmt="%I:%M %p",
                        date=self.start.date(),
                        time=self.start.time()
                    ),
                    from_email="reminder@dccaep.org",
                    recipient_list=[student.student.email],
                )

    def test_reminder(self):
        for student in self.student.all():
            if student.student.email:
                send_mail_task.delay(
                    subject="Testing Reminder from the Delgado "
                    "Community College Adult Education Program",
                    message="",
                    html_message="<p>Hi, {student}</p><p>This message is "
                    "to remind you that you have signed up for a testing "
                    "appointment on {date:{dfmt}} at {time:{tfmt}}."
                    ". Please call 504-671-5434 or email adulted@dcc.edu "
                    "if you have any questions or need to reschedule.</p>"
                    "<br><p>Thank you,</p>"
                    "<p>The Adult Education Program</p>"
                    "<p>Delgado Community College</p>".format(
                        student=student.student.first_name,
                        dfmt='%m-%d-%Y',
                        tfmt="%I:%M %p",
                        date=self.start.date(),
                        time=self.start.time()
                    ),
                    from_email="reminder@dccaep.org",
                    recipient_list=[student.student.email],
                )


class TestAppointment(models.Model):

    student = models.ForeignKey(
        Student,
        models.CASCADE,
        related_name='test_appointments'
    )

    event = models.ForeignKey(
        TestEvent,
        models.CASCADE,
        related_name='students'
    )

    notes = models.CharField(
        max_length=20,
        blank=True
    )

    PRESENT = 'P'
    ABSENT = 'A'
    PENDING = 'X'
    TYPE_CHOICES = (
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
        (PENDING, 'Pending'),
    )
    attendance_type = models.CharField(
        max_length=1,
        choices=TYPE_CHOICES,
        default=PENDING
    )
    attendance_date = models.DateField(
        null=True,
        blank=True
    )
    time_in = models.TimeField(
        blank=True,
        null=True
    )
    time_out = models.TimeField(
        blank=True,
        null=True
    )
    att_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Testing Appointment"
        verbose_name_plural = "Testing Appointments"
        unique_together = ('student', 'event')

    def __str__(self):
        return self.student.__str__() + " for " + self.event.__str__()

    def get_absolute_url(self):
        return reverse(
            "assessments:test appointment detail",
            kwargs={'pk': self.pk}
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

    def save(self, *args, **kwargs):
        self.event.check_full()
        super(TestAppointment, self).save(*args, **kwargs)


class TestHistory(models.Model):

    student = models.OneToOneField(
        Student,
        models.CASCADE,
        related_name="tests"
    )

    student_wru = models.CharField(
        max_length=8,
        blank=True
    )

    last_test = models.DateField(
        blank=True,
        null=True
    )

    test_assignment = models.CharField(
        max_length=10,
        blank=True
    )

    class Meta:
        verbose_name = "Test History"
        verbose_name_plural = "Testing Histories"

    def __str__(self):
        return " | ".join([self.student.WRU_ID, self.student.__str__()])

    def get_absolute_url(self):
        return reverse(
            "assessments:student test history",
            kwargs={'slug': self.student.slug}
        )

    def has_pretest(self):
        return self.last_test > date.today() - timedelta(days=150)

    def update_status(self, test):
        if not self.last_test:
            self.last_test = test.test_date
        else:
            if self.last_test <= test.test_date:
                self.last_test = test.test_date
        self.test_assignment = test.assign()
        self.save()

    def active_hours(self):
        attendance_set = Attendance.objects.filter(
            enrollment__student=self.student,
            attendance_date__gte=self.last_test,
            attendance_type='P'
        )

        total_hours = 0

        for attendance in attendance_set:
            total_hours += attendance.hours()
        return total_hours

    @property
    def latest_tabe(self):
        return self.tabe_tests.latest('test_date')

    @property
    def latest_clas_e(self):
        return self.clas_e_tests.latest('test_date')

    @property
    def latest_gain(self):
        return self.gain_tests.latest('test_date')

    @property
    def latest_hiset_practice(self):
        date = self.hiset_practice_tests.latest('test_date').test_date
        return self.hiset_practice_tests.filter(test_date=date)


class Test(models.Model):

    student = models.ForeignKey(
        TestHistory,
        models.PROTECT,
        related_name="%(class)s_tests"
    )

    test_date = models.DateField()

    class Meta:
        abstract = True


class NRSTest(Test):

    reported = models.BooleanField(
        default=False
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(Test, self).save(*args, **kwargs)
        self.student.update_status(self)


class Tabe(NRSTest):

    NINE = '9'
    TEN = '10'
    ELEVEN = '11'
    TWELVE = '12'
    FORM_CHOICES = (
        (NINE, '9'),
        (TEN, '10'),
        (ELEVEN, '11'),
        (TWELVE, '12')
    )

    A = "A"
    D = "D"
    M = "M"
    E = "E"
    L = "L"
    LEVEL_CHOICES = (
        (A, "A"),
        (D, "D"),
        (M, "M"),
        (E, "E"),
        (L, "L")
    )

    form = models.CharField(
        max_length=2,
        choices=FORM_CHOICES
    )

    read_level = models.CharField(
        max_length=1,
        choices=LEVEL_CHOICES,
    )

    math_level = models.CharField(
        max_length=1,
        choices=LEVEL_CHOICES,
    )

    lang_level = models.CharField(
        max_length=1,
        choices=LEVEL_CHOICES,
    )

    read_ss = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )

    math_comp_ss = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )

    app_math_ss = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )

    lang_ss = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )

    total_math_ss = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )

    total_batt_ss = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )

    read_ge = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True
    )

    math_comp_ge = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True
    )

    app_math_ge = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True
    )

    lang_ge = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True
    )

    total_math_ge = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True
    )

    total_batt_ge = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True
    )

    read_nrs = models.CharField(
        max_length=1,
        blank=True,
        null=True
    )

    math_nrs = models.CharField(
        max_length=1,
        blank=True,
        null=True
    )

    lang_nrs = models.CharField(
        max_length=1,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "TABE"
        verbose_name_plural = "TABE scores"

    def __str__(self):
        student = self.student.__str__()
        date = str(self.test_date)
        return " | ".join([student, 'TABE', date])

    def get_absolute_url(self):
        return reverse(
            "assessments:student tabe detail",
            kwargs={
                'slug': self.student.student.slug,
                'pk': self.pk
            }
        )

    @staticmethod
    def get_level(score, level, subject):
        table = {
            "read":(501, 536, 576, 800),
            "math":(496, 537, 596, 800),
            "lang":(511, 547, 584, 800)
        }
        if score is None:
            level = "-"
        elif score < table[subject][0]:
            level = "E"
        elif score < table[subject][1]:
            level = "M"
        elif score < table[subject][2]:
            level = "D"
        elif score < table[subject][3]:
            level = "A"
        else:
            level = "*"
        return level

    def assign(self):
        if self.form == "11":
            form = "12"
        else:
            form = "11"
        r_level = self.get_level(self.read_ss, self.read_level, 'read')
        m_level = self.get_level(self.total_math_ss, self.math_level, 'math')
        l_level = self.get_level(self.lang_ss, self.lang_level, 'lang')

        return " ".join([form, r_level, m_level, l_level])


class Tabe_Loc(NRSTest):

    read = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )

    math_comp = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )

    app_math = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )

    lang = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )

    composite = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "TABE Locator"
        verbose_name_plural = "TABE Locators"

    def __str__(self):
        student = self.student.__str__()
        date = str(self.test_date)
        return " | ".join([student, 'TABE Loc', date])

    def assign(self):
        if 9 > self.composite > 6:
            assignment = "M"
        elif 11 > self.composite > 8:
            assignment = "D"
        elif self.composite > 10:
            assignment = "A"
        elif self.composite < 7:
            assignment = "E"
        else:
            assignment = "M"
        return assignment


class Clas_E(NRSTest):

    A = "A"
    B = "B"
    FORM_CHOICES = (
        (A, "A"),
        (B, "B")
    )

    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    LEVEL_CHOICES = (
        (ONE, "1"),
        (TWO, "2"),
        (THREE, "3"),
        (FOUR, "4")
    )

    form = models.CharField(
        max_length=1,
        choices=FORM_CHOICES
    )

    read_level = models.CharField(
        max_length=1,
        choices=LEVEL_CHOICES,
    )

    read_ss = models.PositiveSmallIntegerField(
    )

    read_nrs = models.CharField(
        max_length=1,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "CLAS-E"
        verbose_name_plural = "CLAS-E scores"


    def __str__(self):
        student = self.student.__str__()
        date = str(self.test_date)
        return " | ".join([student, 'CLAS-E', date])

    def get_absolute_url(self):
        return reverse(
            "assessments:student clas-e detail",
            kwargs={
                'slug': self.student.student.slug,
                'pk': self.pk
            }
        )

    def assign(self):
        assignment_dict = {
            "1": (441, 560, 0, 0),
            "2": (400, 450, 500, 620),
            "3": (400, 450, 504, 650),
            "4": (360, 473, 510, 554)
        }
        a = assignment_dict[self.read_level]
        if self.form.upper() == 'A':
            form = 'B'
        else:
            form = 'A'
        if self.read_ss <= a[0]:
            level = "1"
        elif self.read_ss <= a[1]:
            level = "2"
        elif self.read_ss <= a[2]:
            level = "3"
        elif self.read_ss <= a[3]:
            level = "4"
        else:
            return "11 M"
        return " ".join([level, form])


class Clas_E_Loc(NRSTest):

    read = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "CLAS-E Locator"
        verbose_name_plural = "CLAS-E Locators"

    def __str__(self):
        student = self.student.__str__()
        date = str(self.test_date)
        return " | ".join([student, 'CLAS-E Loc', date])

    def assign(self):
        if self.read > 12:
            assignment = "4"
        elif self.read > 9:
            assignment = "3"
        elif self.read > 6:
            assignment = "2"
        else:
            assignment = "1"
        return assignment


class Gain(NRSTest):

    A = 'A'
    B = 'B'
    FORM_CHOICES = (
        (A, 'A'),
        (B, 'B'),
    )

    MATH = 'Math'
    ENGLISH = 'English'
    SUBJECT_CHOICES = (
        (MATH, 'Math'),
        (ENGLISH, 'English')
    )

    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    NRS_CHOICES = (
        (ONE, "1"),
        (TWO, "2"),
        (THREE, "3"),
        (FOUR, "4"),
        (FIVE, "5"),
        (SIX, "6"),
    )

    form = models.CharField(
        max_length=1,
        choices=FORM_CHOICES
    )

    subject = models.CharField(
        max_length=7,
        choices=SUBJECT_CHOICES
    )

    scale_score = models.PositiveSmallIntegerField(
    )

    grade_eq = models.DecimalField(
        max_digits=3,
        decimal_places=1
    )

    nrs = models.CharField(
        max_length=1,
        choices=NRS_CHOICES
    )

    class Meta:
        verbose_name = 'GAIN'
        verbose_name_plural = "GAIN Scores"

    def __str__(self):
        student = self.student.__str__()
        date = str(self.test_date)
        return " | ".join([student, 'GAIN', date])

    def assign(self):
        return "GAIN"


class HiSet_Practice(Test):

    MATH = 'Math'
    READING = 'Reading'
    SCIENCE = 'Science'
    SOCIAL_STUDIES = 'Social Studies'
    WRITING = 'Writing'
    ESSAY = 'Essay'
    SUBJECT_CHOICES = (
        (MATH, 'Math'),
        (READING, 'Reading'),
        (SCIENCE, 'Science'),
        (SOCIAL_STUDIES, 'Social Studies'),
        (WRITING, 'Writing'),
        (ESSAY, 'Essay'),
    )

    N = 'Not yet prepared'
    S = 'Somewhat prepared'
    P = 'Prepared'
    W = 'Well Prepared'
    GRADE_CHOICES = (
        (N, 'Not yet prepared'),
        (S, 'Somewhat prepared'),
        (P, 'Prepared'),
        (W, 'Well Prepared'),
    )

    FPT2 = 'FPT2'
    FPT3 = 'FPT3'
    PPT2 = 'PPT2'
    PPT3 = 'PPT3'
    PPT4 = 'PPT4'
    PPT5 = 'PPT5'
    OPT2 = 'OPT2'
    OPT3 = 'OPT3'
    FPT6A = 'FPT6A'
    PPT6A = 'PPT6A'
    OPT6A = 'OPT6A'
    FPT7 = 'FPT7'
    OPT7 = 'OPT7'
    OPT8 = 'OPT8'

    VERSION_CHOICES = (
        (FPT2, 'Free Practice Test 2 (2015)'),
        (FPT3, 'Free Practice Test 3 (2015)'),
        (PPT2, 'Paid Practice Test 2 (2015)'),
        (PPT3, 'Paid Practice Test 3 (2015)'),
        (PPT4, 'Paid Practice Test 4 (2015)'),
        (PPT5, 'Paid Practice Test 5 (2015)'),
        (OPT2, 'Official Practice Test 2 (2015)'),
        (OPT3, 'Official Practice Test 3 (2015)'),
        (FPT6A, 'Free Practice Test 6A (2016)'),
        (PPT6A, 'Paid Practice Test 6A (2016)'),
        (OPT6A, 'Official Practice Test 6A (2016)'),
        (FPT7, 'Free Practice Test 7 (2017)'),
        (OPT7, 'Official Practice Test 7 (2017)'),
        (OPT8, 'Official Practice Test 8 (2018)'),
    )

    STAFF = 'Staff'
    SELF = 'Self'

    PROCTOR_CHOICES = (
        (STAFF, 'Proctored by Staff Member'),
        (SELF, 'Self-Administered'),
    )

    subject = models.CharField(
        max_length=14,
        choices=SUBJECT_CHOICES
    )

    grade = models.CharField(
        max_length=17,
        choices=GRADE_CHOICES
    )

    test_version = models.CharField(
        max_length=5,
        choices=VERSION_CHOICES,
        blank=True
    )

    proctor = models.CharField(
        max_length=5,
        choices=PROCTOR_CHOICES,
        default="Staff"
    )

    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.PROTECT,
        related_name='hpt_submissions'
    )

    score = models.PositiveSmallIntegerField(
    )

    class Meta:
        verbose_name = "HiSET Practice"
        verbose_name_plural = "HiSET Practice scores"

    def __str__(self):
        student = self.student.__str__()
        date = str(self.test_date)
        return " | ".join([student, 'HiSET Practice', date])

    def get_absolute_url(self):
        return reverse(
            "assessments:student hiset practice detail",
            kwargs={
                'slug': self.student.student.slug,
                'pk': self.pk
            }
        )
