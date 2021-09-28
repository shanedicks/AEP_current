from datetime import datetime, timedelta
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls import reverse
from core.tasks import send_mail_task, send_sms_task
from sections.tasks import roster_to_classroom_task
from .tasks import enforce_attendance_task

Q = models.Q

class Semester(models.Model):

    title = models.CharField(max_length=40)
    start_date = models.DateField()
    end_date = models.DateField()

    allowed_absences = models.SmallIntegerField(default=4)

    class Meta:
        ordering = ['-end_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('semesters:semester detail', kwargs={'pk': self.pk})

    def get_days(self):
        return self.days.all()

    def get_sections(self):
        return self.sections.all()

    def get_enrollment_queryset(self):
        Enrollment = apps.get_model('sections', 'Enrollment')
        return Enrollment.objects.filter(section__semester=self)

    def get_attendance_queryset(self):
        Attendance = apps.get_model('sections', 'Attendance')
        return Attendance.objects.filter(enrollment__section__semester=self)

    @property
    def section_count(self):
        return self.sections.all().count()

    @property
    def unique_student_count(self):
        return self.get_enrollment_queryset().distinct('student').count()   

    @property
    def enrollment_count(self):
        return self.get_enrollment_queryset().count()

    @property
    def completed_enrollment_count(self):
        return self.get_enrollment_queryset().filter(status='C').count()

    @property
    def dropped_enrollment_count(self):
        return self.get_enrollment_queryset().filter(status='D').count()

    @property
    def total_attendance_count(self):
        return self.get_attendance_queryset().count()

    @property
    def present_attendance_count(self):
        return self.get_attendance_queryset().filter(attendance_type='P').count()

    @property
    def absent_attendance_count(self):
        return self.get_attendance_queryset().filter(attendance_type='A').count()

    @property
    def cancelled_attendance_count(self):
        return self.get_attendance_queryset().filter(attendance_type='C').count()

    @property
    def total_enrolled_hours(self):
        return sum([att.enrolled_hours for att in self.get_attendance_queryset()])

    @property
    def total_attended_hours(self):
        return sum([att.hours for att in self.get_attendance_queryset()])

    def begin(self):
        for section in self.get_sections():
            section.begin()

    def end(self):
        for section in self.get_sections():
            section.end()

    def attendance_reminder(self):
        for section in self.get_sections():
            section.attendance_reminder()

    def waitlist(self):
        for section in self.get_sections():
            section.waitlist_update()

    def enforce_attendance(self):
        for section in self.get_sections():
            enforce_attendance_task.delay(section.id)

    def g_suite_attendance(self):
        for section in self.get_sections():
            section.g_suite_attendance()

    def roster_to_classroom(self):
        for section in self.get_sections():
            roster_to_classroom_task.delay(section.id)

    def validate_enrollments(self):
        partner_check = ['', 'Job1', 'JeffPar']
        students = self.get_enrollment_queryset().filter(
            status='A',
            student__partner__in=partner_check
        )
        cutoff = datetime.today().date() - timedelta(days=180)
        to_hold = students.filter(
            Q(student__tests__last_test_date__lte=cutoff) | Q(student__tests__last_test_date=None)
        )
        to_hold.update(status='W')

    def refresh_enrollments(self):
        students = self.get_enrollment_queryset().filter(status='W')
        cutoff = datetime.today().date() - timedelta(days=180)
        to_refresh = students.filter(student__tests__last_test_date__gte=cutoff)
        to_refresh.update(status='A')


class Survey(models.Model):

    title = models.CharField(
        max_length=100
    )

    form_link = models.URLField(
        blank=True
    )

    sessions = models.ManyToManyField(
        Semester,
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def send_survey(self):
        sessions = self.sessions.all()
        students = apps.get_model('people', 'Student').objects.filter(
            classes__section__semester__in=sessions
        ).distinct()
        for student in students:
            try:
                g_suite_email = student.elearn_record.g_suite_email
            except ObjectDoesNotExist:
                g_suite_email = ''
            emails = [g_suite_email, student.email]
            recipients = [email for email in emails if email != '']
            send_mail_task.delay(
                subject="Delgado Adult Education - We want to hear from you!",
                message="",
                html_message="""<p>Hi {first_name},</p><p>Would you be able 
                to help us out by answering a few questions? If so, please 
                <a href='{form_link}'>click here</a> to access our survey. 
                If the form asks for it, please enter your workreadyu id: 
                {wru}</p><p>Thanks so much for taking the time to help us</p><br>
                <p>¿Podrías ayudarnos respondiendo algunas preguntas? Si es así, 
                haga <a href='{form_link}'>clic aquí</a> para acceder a nuestra 
                encuesta. Si el formulario lo solicita, ingrese su id de 
                workreadyu: {wru}</p><p>Muchas gracias por tomarse el tiempo 
                para ayudarnos.</p>
                """.format(
                    first_name=student.first_name,
                    form_link=self.form_link,
                    wru=student.WRU_ID
                ),
                from_email="survey_robot@dccaep.org",
                recipient_list=recipients
            )

class Message(models.Model):

    title = models.CharField(
        max_length=100
    )

    sessions = models.ManyToManyField(
        Semester,
    )

    message = models.CharField(
        max_length=160
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def send_message(self):
        sessions = self.sessions.all()
        students = apps.get_model('people', 'Student').objects.filter(
            classes__section__semester__in=sessions
        ).distinct()
        for student in students:
            send_sms_task.delay(
                dst=student.phone,
                message=self.message
            )
        

class Day(models.Model):

    date = models.DateField()
    semester = models.ForeignKey(
        Semester,
        models.CASCADE,
        related_name='days'
    )
    notes = models.TextField(
        blank=True,
        max_length=250
    )
