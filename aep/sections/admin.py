from django.contrib import admin
from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from people.models import Staff
from .models import Section, Enrollment, Attendance


class SectionResource(resources.ModelResource):

    class Meta:
        model = Section
        fields = (
            'id',
            'title',
            'semester',
            'teacher',
            'site',
            'room',
            'program',
            'seats',
            'start_time',
            'end_time',
            'WRU_ID',
            'monday',
            'tuesday',
            'wednesday',
            'thursday',
            'friday',
            'saturday',
            'sunday'
        )


class SectionAdmin(ImportExportModelAdmin):

    resource_class = SectionResource

    list_display = (
        "title",
        "WRU_ID",
        "program",
        "site",
        "teacher",
        "get_days_str",
        "seats",
        "start_time",
        "end_time",
        'semester'

    )

    search_fields = ["title", "program", 'site']

    actions = ["begin", "enforce_attendance"]

    def begin(self, request, queryset):
        for obj in queryset:
            obj.begin()

    def enforce_attendance(self, request, queryset):
        for obj in queryset:
            obj.enforce_attendance()


admin.site.register(Section, SectionAdmin)


class EnrollmentResource(resources.ModelResource):

    class Meta:
        model = Enrollment
        fields = (
            "section__WRU_ID",
            "section__title",
            "student__WRU_ID",
            "student__user__last_name",
            "student__user__first_name",
            "created"
        )


class EnrollmentAdmin(ImportExportModelAdmin):

    resource_class = EnrollmentResource

    list_display = (
        '__str__',
        'section',
        'student',
        'creator',
        'created',
        'last_modified'
    )

    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "section__title"
    ]

    fields = (
        'status',
    )

    actions = ['activate']

    def activate(self, request, queryset):
        for obj in queryset:
            self.activate()


admin.site.register(Enrollment, EnrollmentAdmin)

class AttendanceResource(resources.ModelResource):

    class Meta:
        model = Attendance
        fields = (
            "enrollment__student__WRU_ID",
            "enrollment__student__user__last_name",
            "enrollment__student__user__first_name",
            "enrollment__section__WRU_ID",
            "attendance_type",
            "attendance_date",
            "time_in",
            "time_out",
        )

class AttendanceAdmin(ImportExportActionModelAdmin):

    resource_class = AttendanceResource

    list_display = (
        '__str__',
        'attendance_date',
        'attendance_type',
    )

    search_fields = (
        'enrollment__student__user__first_name',
        'enrollment__student__user__last_name',
        'enrollment__section__title',
        'attendance_date',
    )

    fields = (
        'attendance_type',
        'attendance_date',
        'time_in',
        'time_out'
    )

admin.site.register(Attendance, AttendanceAdmin)
