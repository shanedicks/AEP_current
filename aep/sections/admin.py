from django.contrib import admin

from .models import Section, Enrollment, Attendance

admin.site.register(Section)
admin.site.register(Enrollment)
admin.site.register(Attendance)
