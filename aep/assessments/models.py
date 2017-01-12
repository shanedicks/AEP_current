from django.db import models
from django.core.urlresolvers import reverse
from people.models import Staff, Student


class TestEvent(models.Model):

    TABE = 'TABE'
    CLAS_E = 'CLAS-E'
    TABE_LOC = 'TABE Locator'
    CLAS_E_LOC = 'CLAS-E Locator'
    HISET_PRACTICE = 'HiSET Practice'
    EXIT_EXAM = 'Exit Exam'
    TEST_CHOICES = (
        (TABE, 'TABE Test'),
        (TABE_LOC, 'TABE Locator'),
        (CLAS_E, 'CLAS-E Test'),
        (CLAS_E_LOC, 'CLAS-E Locator'),
        (HISET_PRACTICE, 'HiSET Practice'),
        (EXIT_EXAM, 'Exit Exam')
    )

    proctor = models.ForeignKey(
        Staff,
        related_name="Tests",
        blank=True,
        null=True
    )

    test = models.CharField(
        choices=TEST_CHOICES,
        max_length=20
    )

    seats = models.PositiveSmallIntegerField()

    start = models.DateTimeField()

    end = models.DateTimeField()

    class Meta:
        verbose_name = "Test Event"
        verbose_name_plural = "Test Events"

    def __str__(self):
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
            return self.seats - self.students
        return None

    def is_full(self):
        return self.open_seats < 1


class TestAppointment(models.Model):

    student = models.ForeignKey(
        Student,
        related_name='test_appointments'
    )

    event = models.ForeignKey(
        TestEvent,
        related_name='students'
    )

    class Meta:
        verbose_name = "Testing Appointment"
        verbose_name_plural = "Testing Appointments"

    def __str__(self):
        return self.student.__str__() + " for " + self.event.__str__()

    def get_absolute_url(self):
        return reverse(
            "assessments:test appointment detail",
            kwargs={'slug': self.student.slug}
        )


class TestHistory(models.Model):

    student = models.OneToOneField(
        Student,
        related_name="tests"
    )

    current_pretest = models.BooleanField(
        default=False
    )

    last_test = models.DateField(
        blank=True,
        null=True
    )

    hours = models.PositiveSmallIntegerField(
        default=0
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


class Test(models.Model):

    student = models.ForeignKey(
        TestHistory,
        related_name='%(class)s_tests'
    )

    student_wru = models.CharField(
        blank=True,
        max_length=8,
        unique=True
    )

    test_date = models.DateField()

    class Meta:
        abstract = True


class Tabe(Test):

    NINE = '9'
    TEN = '10'
    FORM_CHOICES = (
        (NINE, '9'),
        (TEN, '10')
    )

    A = "A"
    D = "D"
    M = "M"
    E = "E"
    LEVEL_CHOICES = (
        (A, "A"),
        (D, "D"),
        (M, "M"),
        (E, "E")
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


class Tabe_Loc(Test):

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
        student = self.student.__str()
        date = str(self.test_date)
        return " | ".join([student, 'TABE Loc', date])


class Clas_E(Test):

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
        student = self.student.__str()
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


class Clas_E_Loc(Test):

    read = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "CLAS-E Locator"
        verbose_name_plural = "CLAS-E Locators"

    def __str__(self):
        student = self.student.__str()
        date = str(self.test_date)
        return " | ".join([student, 'CLAS-E Loc', date])


class HiSet_Practice(Test):

    class Meta:
        verbose_name = "HiSET Practice"
        verbose_name_plural = "HiSET Practice scores"

    def __str__(self):
        student = self.student.__str()
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
