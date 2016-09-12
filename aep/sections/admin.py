from django.contrib import admin

from .models import Semester, Section, Enrollment, Attendance

admin.site.register(Semester)
admin.site.register(Section)
admin.site.register(Enrollment)
admin.site.register(Attendance)
