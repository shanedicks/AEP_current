from datetime import timedelta
from django.contrib import admin
from django.utils import timezone
from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from people.models import Student
from .models import TestEvent, TestHistory, TestAppointment, Tabe, Tabe_Loc, Clas_E, Clas_E_Loc, Gain, HiSET, HiSet_Practice, Message
from .tasks import (event_attendance_report_task, test_process_task, 
    orientation_reminder_task, test_reminder_task, send_message_task,
    send_score_report_link_task, send_link_task)


class TestEventAdmin(admin.ModelAdmin):

    list_display = (
        '__str__',
        'test',
        'proctor',
        'site',
        'room',
        'seats',
        'start',
        'end',
        'full'
    )

    list_filter = (
        'start',
        'test',
        'site'
    )

    search_fields = [
        'title',
        'test',
        'start',
        'proctor__last_name',
        'proctor__first_name',
        'site__code',
        'site__name'
    ]

    fields = (
        'title',
        'test',
        'proctor',
        'site',
        'room',
        'seats',
        'start',
        'end',
        'full',
        'hidden'
    )

    autocomplete_fields = [
        "proctor"
    ]

    actions = [
        "orientation_reminder",
        "test_reminder",
        "attendance_report",
        'send_paperwork_form_link',
        'send_photo_id_form_link'
    ]

    def orientation_reminder(self, request, queryset):
        for obj in queryset:
            orientation_reminder_task.delay(obj.id)

    def test_reminder(self, request, queryset):
        for obj in queryset:
            test_reminder_task.delay(obj.id)

    def attendance_report(self, request, queryset):
        for obj in queryset:
            event_attendance_report_task.delay(obj.id, request.user.email)

    def send_paperwork_form_link(self, request, queryset):
        for obj in queryset:
            send_link_task.delay(obj.id, 'sign paperwork')

    def send_photo_id_form_link(self, request, queryset):
        for obj in queryset:
            send_link_task.delay(obj.id, 'upload photo id')


admin.site.register(TestEvent, TestEventAdmin)


class TestAppointmentResource(resources.ModelResource):

    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=widgets.ForeignKeyWidget(Student, 'WRU_ID')
    )

    class Meta:
        model = TestAppointment
        fields = (
            'id',
            'student',
            'event',
            'attendance_type',
            'attendance_date',
            'att_hours',
            'notes'
        )


class TestAppointmentAdmin(ImportExportActionModelAdmin):

    resource_class = TestAppointmentResource

    list_display = (
        '__str__',
        'attendance_type',
        'att_hours',
        'time_in',
        'time_out'
    )

    list_filter = (
        'attendance_type',
    )

    search_fields = [
        'student__first_name',
        'student__last_name',
        'student__WRU_ID',
        'event__start',
        'event__test',
        'event__title'

    ]

    fields = (
        'student',
        'event',
    )

    readonly_fields = ['student']


admin.site.register(TestAppointment, TestAppointmentAdmin)


class TestHistoryAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'student_wru',
        'last_test_type',
        'last_test_date',
    )

    list_filter = (
        'last_test_date',
    )

    search_fields = [
        'student__first_name',
        'student__last_name',
        'student_wru',
        'last_test_date'
    ]

    fields = (
        ('student',
        'student_wru'),
        'last_test_type',
        'last_test_date',
        'test_assignment'
    )

    readonly_fields = ['student']


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
            'score_report_link'
        )


class TabeAdmin(ImportExportActionModelAdmin):

    resource_class = TabeResource

    list_display = (
        'student',
        'test_date',
        'form',
        'read_level',
        'math_level',
        'lang_level',
        'read_nrs',
        'math_nrs',
        'lang_nrs',
        'score_report_link'
    )

    list_filter = (
        'test_date',
    )

    search_fields = [
        'student__student__first_name',
        'student__student__last_name',
        'student__student__WRU_ID',
        'student__student_wru',
        'test_date'
    ]

    fields = [
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
        'score_report_link'
    ]

    readonly_fields = ['student']

    actions = ImportExportActionModelAdmin.actions + (
        'process_tests',
        'send_score_report'
    )

    def process_tests(self, request, queryset):
        for obj in queryset:
            test_process_task.delay(obj.get_test_type(), obj.id)

    def send_score_report(self, request, queryset):
        for obj in queryset:
            send_score_report_link_task(obj.id, obj.get_test_type())

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
            'write_level',
            'write_ss',
            'write_nrs'
        )


class Clas_E_Admin(ImportExportActionModelAdmin):

    resource_class = Clas_E_Resource

    list_display = (
        'student',
        'test_date',
        'read_nrs',
        'write_nrs',
        'score_report_link'
    )

    list_filter = (
        'test_date',
    )

    search_fields = [
        'student__student__first_name',
        'student__student__last_name',
        'student__student__WRU_ID',
        'student__student_wru',
        'test_date'
    ]

    fields = (
        'student',
        'form',
        'test_date',
        'read_level',
        'read_ss',
        'read_nrs',
        'write_level',
        'write_ss',
        'write_nrs',
        'score_report_link'
    )

    readonly_fields = ['student']

    actions = ImportExportActionModelAdmin.actions + (
        'process_tests',
        'send_score_report'
    )

    def process_tests(self, request, queryset):
        for obj in queryset:
            test_process_task.delay(obj.get_test_type(), obj.id)

    def send_score_report(self, request, queryset):
        for obj in queryset:
            send_score_report_link_task(obj.id, obj.get_test_type())


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
        'student__student__first_name',
        'student__student__last_name',
        'student_wru',
        'test_date'
    ]

    fields = (
        'test_date',
        'read',
        'math_comp',
        'app_math',
        'lang',
        'composite',
        'score_report_link'
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
        'student__student__first_name',
        'student__student__last_name',
        'student_wru',
        'test_date'
    ]

    fields = (
        'test_date',
        'read',
        'score_report_link'
    )


admin.site.register(Clas_E_Loc, Clas_E_Loc_Admin)


class Gain_Resource(TestResource):

    class Meta:
        model = Gain
        fields = (
            'id',
            'student',
            'test_date',
            'form',
            'subject',
            'grade_eq',
            'scale_score',
            'nrs',
        )


class Gain_Admin(ImportExportActionModelAdmin):

    resource_class = Gain_Resource

    list_display = (
        'student',
        'test_date',
        'subject',
        'form',
        'scale_score',
        'grade_eq',
        'nrs'
    )

    list_filter = (
        'test_date',
    )

    search_fields = [
        'student__student__first_name',
        'student__student__last_name',
        'test_date'
    ]

    fields = (
        'student',
        'test_date',
        'form',
        'subject',
        'scale_score',
        'grade_eq',
        'nrs',
        'score_report_link'
    )

    readonly_fields = ['student']

admin.site.register(Gain, Gain_Admin)


class Hiset_Practice_Resource(TestResource):

    class Meta:
        model = HiSet_Practice
        fields = (
            'id',
            'student',
            'student__student__last_name',
            'student__student__first_name',
            'student__student__email',
            'student__student__elearn_record__g_suite_email',
            'test_date',
            'subject',
            'test_version',
            'proctor',
            'reported_by',
            'grade',
            'score',
        )


class Hiset_Practice_Admin(ImportExportActionModelAdmin):

    resource_class = Hiset_Practice_Resource

    list_display = (
        'student',
        'test_date',
        'subject',
        'score',
        'grade',
        'test_version',
        'reported_by'
    )

    list_filter = (
        'test_date',
    )

    search_fields = [
        'student__student__first_name',
        'student__student__last_name',
        'student_wru',
        'test_date'
    ]

    fields = (
        'student',
        'test_date',
        'subject',
        'test_version',
        'proctor',
        'score',
        'grade',

    )

    readonly_fields = ['student']


admin.site.register(HiSet_Practice, Hiset_Practice_Admin)

class Hiset_Resource(TestResource):

    class Meta:
        model = HiSET
        fields = (
            'id',
            'student',
            'student__student__last_name',
            'student__student__first_name',
            'student__student__email',
            'student__student__elearn_record__g_suite_email',
            'test_date',
            'subject',
            'score',
        )


class Hiset_Admin(ImportExportActionModelAdmin):

    resource_class = Hiset_Resource

    list_display = (
        'student',
        'test_date',
        'subject',
        'score',
    )

    list_filter = (
        'test_date',
    )

    search_fields = [
        'student__student__first_name',
        'student__student__last_name',
        'student_wru',
        'test_date'
    ]

    fields = (
        'student',
        'test_date',
        'subject',
        'score',
    )

    readonly_fields = ['student']

admin.site.register(HiSET, Hiset_Admin)

class MessageAdmin(admin.ModelAdmin):

    list_display = [
        "title",
        "sent"
    ]

    filter_horizontal = [
        'events'
    ]

    actions = [
        "send_message"
    ]

    def send_message(self, request, queryset):
        for obj in queryset:
            send_message_task.delay(obj.id)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        request.target = timezone.now() - timedelta(days=180)
        if db_field.name == "events":
            kwargs["queryset"] = TestEvent.objects.filter(start__gte=request.target)
        return super(MessageAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

admin.site.register(Message, MessageAdmin)
