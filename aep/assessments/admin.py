from django.contrib import admin
from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from .models import *

admin.site.register(TestEvent)
admin.site.register(TestAppointment)
admin.site.register(TestHistory)
admin.site.register(Tabe_Loc)
admin.site.register(Clas_E)
admin.site.register(Clas_E_Loc)
admin.site.register(HiSet_Practice)


class TabeResource(resources.ModelResource):

    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=widgets.ForeignKeyWidget(TestHistory, 'student')
    )

    class Meta:
        model = Tabe
        fields = (
            'id',
            'student',
            'student_wru',
            'form',
            'test_date',
            'read_level',
            'math_level',
            'lang_level',
            'read_ss',
            'math_comp_ss',
            'app_math_ss',
            'lang_ss',
            'total_math_ss'
            'total_batt_ss',
            'read_ge',
            'math_comp_ge',
            'app_math_ge',
            'lang_ge',
            'total_math_ge',
            'total_batt_ge',
            'read_nrs',
            'math_nrs',
            'lang_nrs',
        )


class TabeAdmin(ImportExportActionModelAdmin):

    resource_class = TabeResource

    list_display = (
        'student',
        'test_date',
        'read_ge',
        'total_math_ge',
        'lang_ge',
        'total_batt_ge'
    )

    search_fields = [
        'student__user__first_name',
        'student__user__last_name',
        'test_date'
    ]

    fields = [
            'form',
            'test_date',
            'read_level',
            'math_level',
            'lang_level',
            'read_ss',
            'math_comp_ss',
            'app_math_ss',
            'lang_ss',
            'total_math_ss'
            'total_batt_ss',
            'read_ge',
            'math_comp_ge',
            'app_math_ge',
            'lang_ge',
            'total_math_ge',
            'total_batt_ge',
            'read_nrs',
            'math_nrs',
            'lang_nrs',
    ]

admin.site.register(Tabe, TabeAdmin)
