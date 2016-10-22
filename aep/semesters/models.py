from django.db import models


class Semester(models.Model):

    title = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()

    def get_days():
        pass

    def __str__(self):
        return self.title

class Day(models.Model):

    date = models.DateField()
    semester = models.ForeignKey(
        Semester
    )
    notes = models.TextField(
        blank=True,
        max_length=250
    )
