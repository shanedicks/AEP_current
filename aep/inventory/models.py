from django.apps import apps
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

    @property
    def total_items(self):
        return self.items.all().count()

    def in_use(self):
        self.items.filter(
            tickets__issued_date__isnull=False,
            tickets__returned_date__isnull=True,
            )

    def available(self):
        return self.items.exclude(
            tickets__issued_date__isnull=False,
            tickets__returned_date__isnull=True,
            )


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
        return "{0}: {1}".format(self.category.name, self.name)

    def open_tickets(self):
        return self.tickets.filter(
            issued_date__isnull=False,
            returned_date__isnull=True
        )

    def available(self):
        return self.open_tickets().count() == 0


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
