from django.db import models
from django.urls import reverse


class Semester(models.Model):

    title = models.CharField(max_length=20)
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

    @property
    def section_count(self):
        return self.sections.all().count()
 
    def get_enrollments(self):
        sections = self.sections.all()
        students = []
        for section in sections:
            for student in section.students.all():
                students.append(student)
        return students

    @property
    def enrollment_count(self):
        return len(self.get_enrollments())

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
            section.enforce_attendance()

    def g_suite_attendance(self):
        for section in self.get_sections():
            section.g_suite_attendance()


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
