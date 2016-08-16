from django.contrib import admin

from .models import Student, Staff

models = [Student, Staff]
# Register your models here.
admin.site.register(models)
