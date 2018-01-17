from apiclient import discovery
from httplib2 import Http
from django.contrib import admin
from django.conf import settings
from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from oauth2client.service_account import ServiceAccountCredentials
from people.models import Staff, Student
from academics.models import Course
from .models import Section, Enrollment, Attendance


class SectionResource(resources.ModelResource):

    course = fields.Field(
        column_name='course',
        attribute='course',
        widget=widgets.ForeignKeyWidget(Course, 'code')
    )

    class Meta:
        model = Section
        fields = (
            'id',
            'title',
            'semester',
            'teacher',
            'teacher__wru',
            'teacher__last_name',
            'teacher__first_name',
            'g_suite_id',
            'course',
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


class SectionAdmin(ImportExportActionModelAdmin):

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
        'semester',
        'g_suite_id'
    )

    search_fields = ["title", "program", 'site', 'WRU_ID', 'semester__title']

    actions = [
        "begin",
        "enforce_attendance",
        'create_classroom_section',
        'roster_to_classroom'
    ]

    def begin(self, request, queryset):
        for obj in queryset:
            obj.begin()

    def enforce_attendance(self, request, queryset):
        for obj in queryset:
            obj.enforce_attendance()

    def create_classroom_section(self, request, queryset):

        scopes = ['https://www.googleapis.com/auth/classroom.courses']

        credentials = ServiceAccountCredentials._from_parsed_json_keyfile(
            keyfile_dict=settings.KEYFILE_DICT,
            scopes=scopes
        )

        shane = credentials.create_delegated('shane.dicks@elearnclass.org')
        http_auth = shane.authorize(Http())
        service = discovery.build('classroom', 'v1', http=http_auth)

        for obj in queryset:
            if obj.g_suite_id:
                pass
            else:
                record = {
                    "name": obj.title,
                    "section": obj.semester.title,
                    "ownerId": obj.teacher.g_suite_email
                }

                post = service.courses().create(body=record).execute()
                obj.g_suite_id = post.get('id')
                obj.save()

    def assign_teacher(self, request, queryset):

        scopes = ['https://www.googleapis.com/auth/classroom.rosters']

        credentials = ServiceAccountCredentials._from_parsed_json_keyfile(
            keyfile_dict=settings.KEYFILE_DICT,
            scopes=scopes
        )

        shane = credentials.create_delegated('shane.dicks@elearnclass.org')
        http_auth = shane.authorize(Http())
        service = discovery.build('classroom', 'v1', http=http_auth)

    def roster_to_classroom(self, request, queryset):

        scopes = ['https://www.googleapis.com/auth/classroom.rosters']

        credentials = ServiceAccountCredentials._from_parsed_json_keyfile(
            keyfile_dict=settings.KEYFILE_DICT,
            scopes=scopes
        )

        shane = credentials.create_delegated('shane.dicks@elearnclass.org')
        http_auth = shane.authorize(Http())
        service = discovery.build('classroom', 'v1', http=http_auth)

        for obj in queryset:
            students = obj.students.all().prefetch_related(
                'student__elearn_record'
            )
            for student in students:
                s = {
                    "userId": student.student.elearn_record.g_suite_email
                }
                service.courses().students().create(
                    courseId=obj.g_suite_id,
                    body=s
                ).execute()


admin.site.register(Section, SectionAdmin)


class EnrollmentResource(resources.ModelResource):

    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=widgets.ForeignKeyWidget(Student, 'WRU_ID')
    )

    class Meta:
        model = Enrollment
        fields = (
            "id",
            "section",
            "creator",
            "section__WRU_ID",
            "section__title",
            "student__last_name",
            "student__first_name",
            "created"
        )


class EnrollmentAdmin(ImportExportActionModelAdmin):

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
        "student__first_name",
        "student__last_name",
        "section__title"
    ]

    fields = (
        'status',
    )

    actions = ['activate']

    def activate(self, request, queryset):
        for obj in queryset:
            obj.activate()


admin.site.register(Enrollment, EnrollmentAdmin)

class AttendanceResource(resources.ModelResource):

    class Meta:
        model = Attendance
        fields = (
            "enrollment__student__WRU_ID",
            "enrollment__student__last_name",
            "enrollment__student__first_name",
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
        'enrollment__student__first_name',
        'enrollment__student__last_name',
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
