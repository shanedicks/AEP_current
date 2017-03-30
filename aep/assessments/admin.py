from django.contrib import admin
from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from .models import *

admin.site.register(HiSet_Practice)


class TestEventAdmin(admin.ModelAdmin):

    list_display = (
        '__str__',
        'test',
        'proctor',
        'room',
        'seats',
        'start',
        'end',
        'full'
    )

    search_fields = [
        'title',
        'test',
        'proctor',
        'start'
    ]

    fields = (
        'title',
        'test',
        'proctor',
        'room',
        'seats',
        'start',
        'end',
        'full'
    )


admin.site.register(TestEvent, TestEventAdmin)


class TestAppointmentAdmin(admin.ModelAdmin):

    list_display = (
        '__str__',
    )

    search_fields = [
        'student__user__first_name',
        'student__user__last_name',
        'student__WRU_ID',
        'event__start',
        'event__test'

    ]

    fields = (
        'event',
    )


admin.site.register(TestAppointment, TestAppointmentAdmin)


class TestHistoryAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'student_wru',
        'last_test',
    )

    search_fields = [
        'student__user__first_name',
        'student__user__last_name',
        'student_wru',
        'last_test'
    ]

    fields = (
        'student_wru',
        'test_assignment'
    )


admin.site.register(TestHistory, TestHistoryAdmin)


class TestResource(resources.ModelResource):

    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=widgets.ForeignKeyWidget(TestHistory, 'student_wru')
    )


class TabeResource(TestResource):

    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=widgets.ForeignKeyWidget(TestHistory, 'student_wru')
    )

    class Meta:
        model = Tabe
        fields = (
            'id',
            'student',
            'form',
            'test_date',
            'read_level',
            'math_level',
            'lang_level',
            'read_ss',
            'math_comp_ss',
            'app_math_ss',
            'lang_ss',
            'total_math_ss',
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
        'student__student__user__first_name',
        'student__student__user__last_name',
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
        'total_math_ss',
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

class Clas_E_Resource(TestResource):

    class Meta:
        model = Clas_E
        fields = (
            'id',
            'student',
            'form',
            'test_date',
            'read_level',
            'read_ss',
            'read_nrs',
        )


class Clas_E_Admin(ImportExportActionModelAdmin):

    resource_class = Clas_E_Resource

    list_display = (
        'student',
        'test_date',
        'read_nrs'
    )

    search_fields = [
        'student__student__user__first_name',
        'student__student__user__last_name',
        'test_date'
    ]

    fields = (
        'form',
        'test_date',
        'read_level',
        'read_ss',
        'read_nrs'
    )


admin.site.register(Clas_E, Clas_E_Admin)


class Tabe_Loc_Resource(TestResource):

    class Meta:
        model = Tabe_Loc
        fields = (
            'id',
            'student',
            'test_date',
            'read',
            'math_comp',
            'app_math',
            'lang',
            'composite'
        )


class Tabe_Loc_Admin(ImportExportActionModelAdmin):

    resource_class = Tabe_Loc_Resource

    list_display = (
        'student',
        'test_date',
        'read',
        'math_comp',
        'app_math',
        'lang',
        'composite'
    )

    search_fields = [
        'student__student__user__first_name',
        'student__student__user__last_name',
        'test_date'
    ]

    fields = (
        'test_date',
        'read',
        'math_comp',
        'app_math',
        'lang',
        'composite'
    )


admin.site.register(Tabe_Loc, Tabe_Loc_Admin)


class Clas_E_Loc_Resource(TestResource):

    class Meta:
        model = Clas_E_Loc
        fields = (
            'id',
            'student',
            'test_date',
            'read'
        )


class Clas_E_Loc_Admin(ImportExportActionModelAdmin):

    resource_class = Clas_E_Loc_Resource

    list_display = [
        'student',
        'test_date',
        'read'
    ]

    search_fields = [
        'student__student__user__first_name',
        'student__student__user__last_name',
        'test_date'
    ]

    fields = (
        'test_date',
        'read'
    )

admin.site.register(Clas_E_Loc, Clas_E_Loc_Admin)
