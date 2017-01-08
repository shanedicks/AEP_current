from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

admin.site.register(TestEvent)
admin.site.register(TestAppointment)
admin.site.register(TestHistory)
admin.site.register(Tabe)
admin.site.register(Tabe_Loc)
admin.site.register(Clas_E)
admin.site.register(Clas_E_Loc)
admin.site.register(HiSet_Practice)
