from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Section, Enrollment, Attendance


admin.site.register(Attendance)


class SectionAdmin(ImportExportModelAdmin):

    list_display = (
        "title",
        "program",
        "site",
        "teacher",
        "get_days_str",
        "seats",
        "start_time",
        "end_time",
        "__str__",
    )

    search_fields = ["title", "program", 'site']


admin.site.register(Section, SectionAdmin)


class EnrollmentAdmin(ImportExportModelAdmin):

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
        "student__user__first_name",
        "section__title"
    ]


admin.site.register(Enrollment, EnrollmentAdmin)
