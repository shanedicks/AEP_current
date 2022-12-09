from django.db import models

from people.models import Student, Staff


class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        max_length=1000,
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"


class Item(models.Model):

    category = models.ForeignKey(
        Category,
        models.PROTECT,
        related_name = "items"
    )

    name = models.CharField(
        max_length = 100,
        blank=True
    )

    state_tag = models.CharField(
        max_length = 100,
        blank=True
    )

    item_id = models.CharField(
        max_length = 100,
        verbose_name="Serial number or other identifier"
    )

    def __str__(self):
        return "{0}: {1}".format(self.item_id, self.name)


class Ticket(models.Model):

    item = models.ForeignKey(
        Item,
        models.PROTECT,
        related_name='tickets'
    )

    student = models.ForeignKey(
        Student,
        models.PROTECT,
        related_name='tickets',
        null=True,
        blank=True
    )

    staff = models.ForeignKey(
        Staff,
        models.PROTECT,
        related_name='tickets',
        null=True,
        blank=True
    )

    issued_date = models.DateField()

    returned_date = models.DateField(
        null=True,
        blank=True
    )

    return_req_date = models.DateField(
        null=True,
        blank=True
    )

    def __str__(self):
        holder = self.student if self.student else self.staff
        return "{0} to {1} on {2}".format(self.item, holder, self.issued_date)
