from django.db import models

# Create your models here.


class Resource(models.Model):

    title = models.CharField(
        max_length=100
    )

    description = models.TextField(
        max_length=1000
    )

    link = models.URLField()

    def __str__(self):
        return self.title


class Skill(models.Model):

    title = models.CharField(
        max_length=100,
    )

    standard = models.CharField(
        max_length=20,
        blank=True
    )

    description = models.TextField(
        max_length=1000,
        blank=True
    )

    resources = models.ManyToManyField(
        Resource,
        blank=True
    )

    class Meta:
        pass

    def __str__(self):
        return self.title


class Course(models.Model):

    title = models.CharField(
        max_length=60,
    )

    code = models.CharField(
        max_length=6,
        blank=True
    )

    g_suite_id = models.CharField(
        max_length=20,
        blank=True
    )

    description = models.TextField(
        max_length=1000,
        blank=True
    )

    objectives = models.TextField(
        max_length=500,
        blank=True
    )

    skills = models.ManyToManyField(
        Skill,
        blank=True
    )

    resources = models.ManyToManyField(
        Resource,
        blank=True
    )

    class Meta:
        pass

    def __str__(self):
        return self.title
