from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from import_export import resources
from import_export.admin import ImportExportModelAdmin, ImportExportMixin
from .models import Student, Staff, WIOA

# Register your models here.
admin.site.register(Staff)


class UserResource(resources.ModelResource):

    class Meta:
        model = User


class StudentResource(resources.ModelResource):

    class Meta:
        model = Student


class WIOAResource(resources.ModelResource):

    class Meta:
        model = WIOA


class StudentAdmin(ImportExportModelAdmin):

    resource_class = StudentResource

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


class WIOAAdmin(ImportExportModelAdmin):
    resource_class = WIOAResource

    list_display = ("__str__", "get_AEP_ID", "get_WRU_ID")

    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "student__AEP_ID",
        "student__WRU_ID"
    ]

    def get_AEP_ID(self, obj):
        return obj.student.AEP_ID
    get_AEP_ID.admin_order_field = "AEP_ID"
    get_AEP_ID.short_description = "AEP ID"

    def get_WRU_ID(self, obj):
        return obj.student.WRU_ID
    get_WRU_ID.admin_order_field = "WRU_ID"
    get_WRU_ID.short_description = "WRU ID"


admin.site.register(WIOA, WIOAAdmin)


class CustomUserAdmin(ImportExportMixin, UserAdmin):
    resource_class = UserResource

    list_display = ("last_name", "first_name", "email", "username")

    search_fields = [
        "last_name",
        "first_name",
        "email"
    ]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
