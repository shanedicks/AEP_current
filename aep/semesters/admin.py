from django.contrib import admin
from .models import Semester, Day

# Register your models here.


class SemesterAdmin(admin.ModelAdmin):

    list_display = (
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
        "waitlist"
    ]

    def attendance_reminder(self, request, queryset):
        for obj in queryset:
            obj.attendance_reminder()

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


admin.site.register(Semester, SemesterAdmin)
admin.site.register(Day)
