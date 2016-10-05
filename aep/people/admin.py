from django.contrib import admin
from django.contrib.auth.models import User

from import_export import resources
from .models import Student, Staff, WIOA

# Register your models here.
admin.site.register(Staff)
admin.site.register(WIOA)


class UserInline(admin.TabularInline):
    model = User
    extra = 0


class StudentAdmin(admin.ModelAdmin):

    list_display = ("__str__", "AEP_ID", "WRU_ID", "dob")

    search_fields = ["user__first_name", "user__last_name", 'WRU_ID']

    fields = [
        "user",
        ("WRU_ID",
         "AEP_ID"),
        "US_citizen",
        ("gender",
         "marital_status"),
        "slug",
        "intake_date",
        "dob",
        ("phone",
         "alt_phone"),
        ("street_address_1",
         "street_address_2"),
        "city",
        "state",
    ]


admin.site.register(Student, StudentAdmin)


class UserResource(resources.ModelResource):

    class Meta:
        model = User


class StudentResource(resources.ModelResource):

    class Meta:
        model = Student


class WIOAResource(resources.ModelResource):

    class Meta:
        model = WIOA
