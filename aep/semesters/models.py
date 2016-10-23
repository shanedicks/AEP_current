from django.db import models
from django.core.urlresolvers import reverse


class Semester(models.Model):

    title = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()

    def get_days(self):
        return self.days.all()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('semesters:semester detail', kwargs={'pk': self.pk})


class Day(models.Model):

    date = models.DateField()
    semester = models.ForeignKey(
        Semester,
        related_name='days'
    )
    notes = models.TextField(
        blank=True,
        max_length=250
    )
