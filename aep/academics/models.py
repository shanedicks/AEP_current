from django.db import models
from people.models import Student, Staff

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
        max_length = 100
    )

    anchor_standard = models.TextField(
        blank=True
    )

    code = models.CharField(
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
        ordering = ["title"]

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

    skills_view = models.BooleanField(
        default=False
    )

    class Meta:
        pass

    def __str__(self):
        return self.title


class Credential(models.Model):

    title = models.CharField(
        max_length = 100
    )

    description = models.TextField()


class Certification(models.Model):

    student = models.ForeignKey(
        Student,
        models.PROTECT,
        related_name = "%(class)ss"
    )

    cert_date = models.DateField()

    certifier = models.ForeignKey(
        Staff,
        models.PROTECT,
        related_name = "%(class)ss"
    )

    class Meta:
        abstract = True


class CourseCompletion(Certification):

    course = models.ForeignKey(
        Course,
        models.PROTECT,
        related_name = "students"
    )

    class Meta:
        unique_together = ('student', 'course')
        verbose_name_plural = "Course Completions"

    def __str__(self):
        course = self.course.title
        student = self.student.__str__()
        return "{0} completed {1}".format(student, course)


class Certificate(Certification):

    credential = models.ForeignKey(
        Credential,
        models.PROTECT,
        related_name = "students"
    )

    class Meta:
        unique_together = ('student', 'credential')

    def __str__(self):
        credential = self.credential.title
        student = self.student.__str__()
        return "{0} earned {1}".format(student, credential)

class SkillMastery(Certification):

    skill = models.ForeignKey(
        Skill,
        models.PROTECT,
        related_name = "students"
    )

    mastered = models.BooleanField(
        default=False
    )

    class Meta:
        verbose_name_plural = "Skill Masteries"
        unique_together = ('student', 'skill')
        ordering = ['skill']

    def __str__(self):
        skill = self.skill.title
        student = self.student.__str__()
        return "{0} mastered {1}".format(student, skill)
