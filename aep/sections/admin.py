from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Section, Enrollment, Attendance


admin.site.register(Attendance)


class SectionAdmin(ImportExportModelAdmin):

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
        "__str__",
    )

    search_fields = ["title", "program", 'site']


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
        "student__user__first_name",
        "section__title"
    ]

    fields = (
        'status',
    )


admin.site.register(Enrollment, EnrollmentAdmin)
