from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Section, Enrollment, Attendance

admin.site.register(Enrollment)
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
