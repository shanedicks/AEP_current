from django.contrib import admin
from .models import Semester, Day
from .tasks import (send_g_suite_info_task, semester_begin_task,
    validate_enrollments_task, refresh_enrollments_task)

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
        "attendance_reminder",
        "begin",
        "end",
        "enforce_attendance",
        "waitlist",
        "send_g_suite_info",
        "send_course_welcome_email",
        "roster_to_classroom",
        "validate_enrollments",
        "refresh_enrollments"
    ]

    def attendance_reminder(self, request, queryset):
        for obj in queryset:
            obj.attendance_reminder()

    def begin(self, request, queryset):
        for obj in queryset:
            semester_begin_task.delay(obj.id)

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

    def validate_enrollments(self, request, queryset):
        for obj in queryset:
            validate_enrollments_task.delay(obj.id)

    def refresh_enrollments(self, request, queryset):
        for obj in queryset:
            refresh_enrollments_task.delay(obj.id)

admin.site.register(Semester, SemesterAdmin)
admin.site.register(Day)
