from django.contrib import admin
from sections.tasks import wru_sections_export_task
from .models import Semester, Survey, Message
from .tasks import (send_g_suite_info_task, semester_begin_task,
    create_missing_g_suite_task, send_message_task, send_schedules_task,
    send_survey_task, send_link_task, attendance_reminder_task)

# Register your models here.


class SemesterAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'title',
        'start_date',
        'end_date',
        'allowed_absences'
    )

    search_fields = ["title"]

    actions = [
        "begin",
        "end",
        "enforce_attendance",
        "waitlist",
        "send_g_suite_info",
        "send_course_welcome_email",
        "roster_to_classroom",
        "validate_enrollments",
        "refresh_enrollments",
        "create_missing_g_suite",
        'send_schedules',
        'send_paperwork_form_link',
        'send_photo_id_form_link',
        'wru_section_export'
    ]

    def attendance_reminder(self, request, queryset):
        id_list = [obj.id for obj in queryset]
        email = request.user.email
        attendance_reminder_task.delay(id_list, email)

    def begin(self, request, queryset):
        for obj in queryset:
            obj.begin()

    def end(self, request, queryset):
        for obj in queryset:
            obj.end()

    def enforce_attendance(self, request, queryset):
        for obj in queryset:
            obj.enforce_attendance()

    def waitlist(self, request, queryset):
        for obj in queryset:
            obj.waitlist()

    def send_g_suite_info(self, request, queryset):
        for obj in queryset:
            send_g_suite_info_task.delay(obj.id)

    def send_course_welcome_email(self, request, queryset):
        for obj in queryset:
            for student in obj.get_enrollment_queryset().distinct('student'):
                student.welcome_email()

    def roster_to_classroom(self,request, queryset):
        for obj in queryset:
            obj.roster_to_classroom()

    def create_missing_g_suite(self, request, queryset):
        for obj in queryset:
            create_missing_g_suite_task.delay(obj.id)

    def send_schedules(self, request, queryset):
        send_schedules_task.delay([obj.id for obj in queryset])

    def send_paperwork_form_link(self, request, queryset):
        for obj in queryset:
            send_link_task.delay(obj.id, 'sign paperwork')

    def send_photo_id_form_link(self, request, queryset):
        for obj in queryset:
            send_link_task.delay(obj.id, 'upload photo id')

    def wru_section_export(self, request, queryset):
        semesters = [obj.id for obj in queryset]
        wru_sections_export_task.delay(request.user.email, semesters)

admin.site.register(Semester, SemesterAdmin)

class SurveyAdmin(admin.ModelAdmin):

    list_display = [
        "title",
    ]

    actions = [
        "send_survey"
    ]

    def send_survey(self, request, queryset):
        for obj in queryset:
            send_survey_task.delay(obj.id)

admin.site.register(Survey, SurveyAdmin)

class MessageAdmin(admin.ModelAdmin):

    list_display = [
        "title",
        "sent"
    ]

    actions = [
        "send_message"
    ]

    def send_message(self, request, queryset):
        for obj in queryset:
            send_message_task.delay(obj.id)

admin.site.register(Message, MessageAdmin)
