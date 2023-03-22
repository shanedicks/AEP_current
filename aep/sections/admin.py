from apiclient import discovery
from httplib2 import Http
from datetime import timedelta
from django.contrib import admin
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from oauth2client.service_account import ServiceAccountCredentials
from people.models import Staff, Student
from academics.models import Course
from .models import Site, Section, Enrollment, Attendance, Message, Cancellation
from .tasks import (roster_to_classroom_task, send_g_suite_info_task, cancel_class_task, add_TA_task,
    create_missing_g_suite_task, create_classroom_section_task, send_message_task, send_link_task)

class SiteResource(resources.ModelResource):

    class Meta:
        model = Site
        fields = (
            'id',
            'code',
            'name',
            'street_address',
            'state',
            'zip_code'
        )

class SiteAdmin(ImportExportModelAdmin):

    resource_class = SiteResource

    list_display = (
            'code',
            'name',
            'street_address',
            'state',
            'zip_code'
        )

admin.site.register(Site, SiteAdmin)

class SectionResource(resources.ModelResource):

    course = fields.Field(
        column_name='course',
        attribute='course',
        widget=widgets.ForeignKeyWidget(Course, 'code')
    )

    site = fields.Field(
        column_name='site',
        attribute='site',
        widget=widgets.ForeignKeyWidget(Site, 'code')
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
            'starting',
            'ending',
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
        'get_site_code',
        "get_teacher",
        "get_days_str",
        "get_active_enrollment_count",
        "start_time",
        "end_time",
        'semester',
        'g_suite_id',
        "get_course_code",
        "program",
    )

    list_filter = (
        'site',
        'program'
    )

    search_fields = [
        "title",
        "program",
        'WRU_ID',
        'semester__title',
        'teacher__first_name',
        'teacher__last_name'
    ]

    autocomplete_fields = [
        "teacher",
        "course"
    ]

    actions = ImportExportActionModelAdmin.actions + (
        "begin",
        "enforce_attendance",
        'create_classroom_section',
        'roster_to_classroom',
        'send_g_suite_info',
        'send_course_welcome_email',
        'add_TA',
        'create_missing_g_suite',
        'send_paperwork_form_link',
        'send_photo_id_form_link'
    )

    def get_active_enrollment_count(self, obj):
        a = obj.students.filter(status="A").count()
        return f"{a} / {obj.seats}"
    get_active_enrollment_count.admin_order_field = "Students"
    get_active_enrollment_count.short_description = "Students"

    def get_course_code(self, obj):
        return getattr(obj.course, 'code', '-')
    get_course_code.short_description = "Course"

    def get_site_code(self, obj):
        return obj.site.code
    get_site_code.short_description = "Site"

    def get_teacher(self, obj):
        return f"{obj.teacher.first_name} {obj.teacher.last_name[0]}"
    get_teacher.short_description = "Teacher"

    def begin(self, request, queryset):
        for obj in queryset:
            obj.begin()

    def enforce_attendance(self, request, queryset):
        for obj in queryset:
            obj.enforce_attendance()

    def create_classroom_section(self, request, queryset):
        section_ids = [obj.id for obj in queryset]
        create_classroom_section_task.delay(section_ids)

    def add_TA(self, request, queryset):
        section_ids = [obj.id for obj in queryset]
        add_TA_task.delay(section_ids)

    def roster_to_classroom(self, request, queryset):
        for obj in queryset:
            roster_to_classroom_task.delay(obj.id)

    def send_g_suite_info(self, request, queryset):
        for obj in queryset:
            send_g_suite_info_task.delay(obj.id)

    def send_course_welcome_email(self, request, queryset):
        for obj in queryset:
            for student in obj.students.all():
                student.welcome_email()

    def send_paperwork_form_link(self, request, queryset):
        for obj in queryset:
            send_link_task.delay(obj.id, 'sign paperwork')

    def send_photo_id_form_link(self, request, queryset):
        for obj in queryset:
            send_link_task.delay(obj.id, 'upload photo id')

    def create_missing_g_suite(self, request, queryset):
        for obj in queryset:
            create_missing_g_suite_task.delay(obj.id)


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
            "status",
            "section__WRU_ID",
            "section__title",
            "student__last_name",
            "student__first_name",
            "student__partner",
            "created",
            "section__semester__title"
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

    list_filter = (
        'status',
        'created'
    )

    search_fields = [
        "student__first_name",
        "student__last_name",
        "student__WRU_ID",
        "section__title",
        "student__partner",
        "section__semester__title"
    ]

    fields = (
        'status',
        "student",
        "section"
    )

    readonly_fields = [
        "student",
        "section",
    ]

    actions = ImportExportActionModelAdmin.actions + ('activate',)

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
            "enrollment__student__partner",
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
        'att_hours'
    )

    list_filter = (
        'attendance_date',
        'attendance_type'
    )

    search_fields = (
        'enrollment__student__first_name',
        'enrollment__student__last_name',
        'enrollment__section__title',
        'attendance_date',
        'enrollment__student__partner'
    )

    fields = (
        'attendance_type',
        'attendance_date',
        'time_in',
        'time_out',
        'att_hours'
    )

admin.site.register(Attendance, AttendanceAdmin)

class MessageAdmin(admin.ModelAdmin):

    list_display = [
        "title",
        "sent"
    ]

    filter_horizontal = ['sections']

    actions = [
        "send_message"
    ]

    def send_message(self, request, queryset):
        for obj in queryset:
            send_message_task.delay(obj.id)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        request.target = timezone.now() - timedelta(days=180)
        if db_field.name == "sections":
            kwargs["queryset"] = Section.objects.filter(semester__start_date__gte=request.target)
        return super(MessageAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

admin.site.register(Message, MessageAdmin)


class CancellationAdmin(admin.ModelAdmin):

    list_display = [
        "section",
        "cancellation_date",
        "cancelled_by"
    ]

    fields = [
        "section",
        "cancellation_date",
        "cancelled_by",
        'send_notification'
    ]

    actions = [
        "do cancellation"
    ]

    def do_cancellation(self, request, queryset):
        for obj in queryset:
            cancel_class_task.delay(obj.id)

    def get_changeform_initial_data(self, request):
        return {"cancelled_by": request.user}

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "cancelled_by":
            kwargs["queryset"] = User.objects.exclude(staff=None).order_by('staff__last_name', 'staff__first_name')
        if db_field.name == "section":
            today = timezone.now().date()
            kwargs["queryset"] = Section.objects.filter(semester__end_date__gte=today) | Section.objects.filter(ending__gte=today)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Cancellation, CancellationAdmin)