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

    search_fields = ["user__first_name", "user__last_name"]


admin.site.register(Student, StudentAdmin)
