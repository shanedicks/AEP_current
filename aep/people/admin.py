from django.contrib import admin
from django.contrib.auth.models import User

from .models import Student, Staff

# Register your models here.
admin.site.register(Staff)


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
