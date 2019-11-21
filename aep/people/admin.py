import requests
import bs4
from datetime import datetime
from django.db import IntegrityError
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ObjectDoesNotExist

from import_export import resources, fields, widgets
from import_export.admin import ImportExportActionModelAdmin, ImportExportMixin
from .models import Student, Staff, WIOA, CollegeInterest
from assessments.models import TestHistory
from coaching.models import ElearnRecord, AceRecord
from core.utils import state_session


class UserResource(resources.ModelResource):

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "username"
        )


class StudentResource(resources.ModelResource):

    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=widgets.ForeignKeyWidget(User, 'username')
    )

    class Meta:
        model = Student
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "alt_email",
            "dob",
            'intake_date',
            "WRU_ID",
            "partner",
            "gender",
            "marital_status",
            "US_citizen",
            "other_ID",
            "ccr_app",
            "esl_app",
            "e_learn_app",
            "ace_app",
            "success_app",
            "phone",
            "alt_phone",
            "street_address_1",
            "street_address_2",
            "city",
            "state",
            "parish",
            "zip_code",
            "emergency_contact",
            "ec_phone",
            "ec_email",
            "ec_relation",
            "paperwork",
            "folder",
            "orientation"
        )


class StaffResource(resources.ModelResource):

    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=widgets.ForeignKeyWidget(User, 'username')
    )

    class Meta:
        model = Staff
        fields = (
            "id",
            'user',
            "first_name",
            "last_name",
            "email",
            'full_time',
            'teacher',
            'coach',
            'active',
            'partner',
            "dob",
            "phone",
            "alt_phone",
            "street_address_1",
            "street_address_2",
            "city",
            "state",
            "zip_code",
            "emergency_contact",
            "ec_phone",
            "ec_email",
            "ec_relation",
            "g_suite_email"
        )


class WIOAResource(resources.ModelResource):

    class Meta:
        model = WIOA
        fields = (
            "id",
            "student__user__id",
            "student__id",
            "student__first_name",
            "student__last_name",
            "student__email",
            "student__WRU_ID",
            "student__dob",
            "student__intake_date",
            "student__gender",
            "student__marital_status",
            "student__US_citizen",
            "student__other_ID",
            "student__ccr_app",
            "student__esl_app",
            "student__prior_registration",
            "student__phone",
            "student__alt_phone",
            "student__street_address_1",
            "student__street_address_2",
            "student__city",
            "student__state",
            "student__parish",
            "student__zip_code",
            "student__emergency_contact",
            "student__ec_phone",
            "student__ec_email",
            "student__ec_relation",
            "SID",
            "hispanic_latino",
            "amer_indian",
            "asian",
            "black",
            "white",
            "pacific_islander",
            "current_employment_status",
            "employer",
            "occupation",
            "migrant_seasonal_status",
            "long_term_unemployed",
            "single_parent",
            "rural_area",
            "displaced_homemaker",
            "dislocated_worker",
            "cult_barriers_hind_emp",
            "in_foster_care",
            "aged_out_foster_care",
            "exhaust_tanf",
            "job_corps",
            "youth_build",
            "recieves_public_assistance",
            "low_family_income",
            "state_payed_foster",
            "disabled_in_poverty",
            "youth_in_high_poverty_area",
            "subject_of_criminal_justice",
            "arrest_record_employment_barrier",
            "lacks_adequate_residence",
            "irregular_sleep_accomodation",
            "migratory_child",
            "runaway_youth",
            "adult_one_stop",
            "youth_one_stop",
            "voc_rehab",
            "wagner_peyser",
            "school_status",
            "recieved_training",
            "etp_name",
            "etp_program",
            "etp_CIP_Code",
            "training_type_1",
            "training_type_2",
            "training_type_3",
            "adhd",
            "autism",
            "deaf_blind",
            "deaf",
            "emotional_disturbance",
            "k12_iep",
            "hard_of_hearing",
            "intellectual_disability",
            "multiple_disabilities",
            "orthopedic_impairment",
            "other_health_impairment",
            "learning_disability",
            "speech_or_lang_impairment",
            "traumatic_brain_injury",
            "visual_impairment",
            "dyscalculia",
            "dysgraphia",
            "dyslexia",
            "neurological_impairments",
            "highest_level_completed",
            "school_location",
            "country",
            "native_language"
        )

        export_order = fields


class StudentAdmin(ImportExportActionModelAdmin):

    resource_class = StudentResource

    list_display = (
        "__str__",
        "WRU_ID",
        "dob",
        "intake_date",
        'paperwork',
        'folder',
        'orientation',
        'partner',
    )

    list_editable = (
        'paperwork',
        'folder',
        'orientation',
    )

    list_filter = (
        'intake_date',
        'partner',
        'paperwork',
        'folder',
        'orientation',
        'e_learn_app',
        'success_app',
        'accuplacer_app',
        'ace_app',
        'ccr_app',
        'esl_app',
        'duplicate',
    )

    search_fields = [
        "first_name",
        "last_name",
        'email',
        'WRU_ID',
        'intake_date',
        'partner',
        'dob'
    ]

    fields = [
        "user",
        "notes",
        "first_name",
        "last_name",
        ("email",
         "alt_email"),
        ("WRU_ID",
         'program'),
        'partner',
        "US_citizen",
        ("gender",
         "marital_status"),
        "slug",
        "intake_date",
        "dob",
        ("phone",
         "alt_phone"),
        ("street_address_1",
         "street_address_2"),
        "city",
        ("state",
         "zip_code"),
        ("duplicate",
         "dupl_date")
    ]

    actions = ImportExportActionModelAdmin.actions + [
        'testify',
        'create_elearn_record',
        'create_ace_record',
        'full_merge'
    ]

    ordering = ['-id']

    def testify(self, request, queryset):
        for obj in queryset:
            obj.testify()

    def create_elearn_record(self, request, queryset):
        for obj in queryset:
            if ElearnRecord.objects.filter(student=obj).exists():
                continue
            else:
                ElearnRecord.objects.create(
                    student=obj,
                    intake_date=datetime.today()
                )

    def create_ace_record(self, request, queryset):
        sem = {
            "1": 'Spring',
            "2": 'Spring',
            "3": 'Spring',
            "4": 'Summer',
            "5": 'Summer',
            "6": 'Summer',
            "7": 'Summer',
            "8": 'Fall',
            "9": 'Fall',
            "10": 'Fall',
            "11": 'Fall',
            "12": 'Spring',
        }
        for obj in queryset:
            if AceRecord.objects.filter(student=obj).exists():
                continue
            else:
                AceRecord.objects.create(
                    student=obj,
                    intake_year=datetime.today().year,
                    intake_semester=sem[str(datetime.today().month)]
                )

    def move_test_history(self, request, queryset):
        q = queryset.order_by('pk')
        try:
            t = q[0].tests
            t.student = q[1]
            try:
                t.save()
            except IntegrityError:
                tabe = q[1].tests.tabe_tests.all()
                tabe.update(student=t)
                tabe_loc = q[1].tests.tabe_loc_tests.all()
                tabe_loc.update(student=t)
                clas_e = q[1].tests.clas_e_tests.all()
                clas_e.update(student=t)
                clas_e_loc = q[1].tests.clas_e_tests.all()
                clas_e_loc.update(student=t)
                gain = q[1].tests.gain_tests.all()
                gain.update(student=t)
                hiset = q[1].tests.hiset_practice_tests.all()
                hiset.update(student=t)
                if t.last_test == None:
                    t.last_test = q[1].tests.last_test
                q[1].tests.delete()
                t.save()
        except ObjectDoesNotExist:
            pass

    def move_classes(self, request, q):
        for c in q[0].classes.all():
            c.student = q[1]
            c.save()

    def move_appointments(self, request, q):
        for a in q[0].test_appointments.all():
            a.student = q[1]
            try:
                a.save()
            except IntegrityError:
                pass

    def move_elearn_record(self, request, q):
        try:
            e = q[1].elearn_record
            pass
        except ObjectDoesNotExist:
            try:
                e = q[0].elearn_record
                e.student = q[1]
                e.save()
            except ObjectDoesNotExist:
                pass

    def move_coaching(self, request, q):
        try:
            p = q[1].coaching_profile
            pass
        except ObjectDoesNotExist:
            try:
                p = q[0].coaching_profile
                p.student = q[1]
                p.save()
            except ObjectDoesNotExist:
                pass
        for c in q[0].coaches.all():
            c.coachee = q[1]
            try:
                c.save()
            except IntegrityError:
                pass

    def move_ace_record(self, request, q):
        try:
            e = q[1].ace_record
            pass
        except ObjectDoesNotExist:
            try:
                a = q[0].ace_record
                a.student = q[1]
                a.save()
            except ObjectDoesNotExist:
                pass

    def move_college_interest(self, request, q):
        try:
            a = q[0].college_interest
            a.student = q[1]
            a.save()
        except ObjectDoesNotExist:
            pass

    def full_merge(self, request, queryset):
        q = queryset.order_by('pk')
        self.move_test_history(request, q)
        self.move_classes(request, q)
        self.move_appointments(request, q)
        self.move_elearn_record(request, q)
        self.move_coaching(request, q)
        self.move_ace_record(request, q)
        self.move_college_interest(request, q)
        n = q[1]
        o = q[0]
        n.intake_date = o.intake_date
        nid = n.WRU_ID
        n.WRU_ID = o.WRU_ID
        n.save()
        o.WRU_ID = 'd' + nid.replace('x', '')
        o.duplicate = True
        o.dupl_date = datetime.today().date()
        o.save()


admin.site.register(Student, StudentAdmin)


class StaffAdmin(ImportExportActionModelAdmin):
    resource_class = StaffResource

    list_display = (
        "user",
        "__str__",
        "wru",
        "phone",
        "email",
        "g_suite_email",
        'teacher',
        'coach',
        'partner'
    )

    list_filter = (
        'active',
        'teacher',
        'full_time',
        'coach',
        'partner'
    )

    search_fields = [
        "first_name",
        "last_name",
    ]


admin.site.register(Staff, StaffAdmin)


class WIOAAdmin(ImportExportActionModelAdmin):

    resource_class = WIOAResource

    list_display = ("__str__", "get_WRU_ID")

    list_filter = ("student__intake_date",)

    search_fields = [
        "student__first_name",
        "student__last_name",
        "student__WRU_ID",
        "student__intake_date"
    ]

    fields = (
        "hispanic_latino",
        "amer_indian",
        "asian",
        "black",
        "white",
        "pacific_islander",
        "current_employment_status",
        "employer",
        "occupation",
        "migrant_seasonal_status",
        "long_term_unemployed",
        "single_parent",
        "rural_area",
        "displaced_homemaker",
        "dislocated_worker",
        "cult_barriers_hind_emp",
        "in_foster_care",
        "aged_out_foster_care",
        "exhaust_tanf",
        "job_corps",
        "youth_build",
        "recieves_public_assistance",
        "low_family_income",
        "state_payed_foster",
        "disabled_in_poverty",
        "youth_in_high_poverty_area",
        "subject_of_criminal_justice",
        "arrest_record_employment_barrier",
        "lacks_adequate_residence",
        "irregular_sleep_accomodation",
        "migratory_child",
        "runaway_youth",
        "adult_one_stop",
        "youth_one_stop",
        "voc_rehab",
        "wagner_peyser",
        "school_status",
        "recieved_training",
        "etp_name",
        "etp_program",
        "etp_CIP_Code",
        "training_type_1",
        "training_type_2",
        "training_type_3",
        "adhd",
        "autism",
        "deaf_blind",
        "deaf",
        "emotional_disturbance",
        "k12_iep",
        "hard_of_hearing",
        "intellectual_disability",
        "multiple_disabilities",
        "orthopedic_impairment",
        "other_health_impairment",
        "learning_disability",
        "speech_or_lang_impairment",
        "traumatic_brain_injury",
        "visual_impairment",
        "dyscalculia",
        "dysgraphia",
        "dyslexia",
        "neurological_impairments",
        "highest_level_completed",
        "school_location",
        "country",
        "native_language",
        "SID"
    )

    actions = ImportExportActionModelAdmin.actions + ['send_to_state', 'check_for_state_id']

    def get_AEP_ID(self, obj):
        return obj.student.AEP_ID
    get_AEP_ID.admin_order_field = "AEP_ID"
    get_AEP_ID.short_description = "AEP ID"

    def get_WRU_ID(self, obj):
        return obj.student.WRU_ID
    get_WRU_ID.admin_order_field = "WRU_ID"
    get_WRU_ID.short_description = "WRU ID"

    def check_for_state_id(self, request, queryset):
        session = state_session()
        for obj in queryset:
            obj.check_for_state_id(session)

    def send_to_state(self, request, queryset):
        session = state_session()
        for obj in queryset:
            obj.send_to_state(session)


admin.site.register(WIOA, WIOAAdmin)


class CustomUserAdmin(ImportExportMixin, UserAdmin):
    resource_class = UserResource

    list_display = ("last_name", "first_name", "email", "username")

    search_fields = [
        "last_name",
        "first_name",
        "email"
    ]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class CollegeInterestAdmin(ImportExportActionModelAdmin):

    fields = [
        'ged_hiset',
        'current_adult_ed',
        'adult_ed_location',
        'bpcc',
        'brcc',
        'ctcc',
        'dcc',
        'ldcc',
        'ftcc',
        'ntcc',
        'ncc',
        'nltc',
        'rpcc',
        'scl',
        'slcc',
        'sowela',
        'lola',
        'other_college',
        'other_college_name',
        'other_college_location',
        'prev_balance',
        'financial_aid',
        'aid_status',
        'nslds_notes',
        'fafsa1617',
        'fafsa1718',
        'fafsa1819',
        'delgado_classes',
        'workforce_training',
        'workforce_training_desc',
        'serv_safe',
        'nccer',
        'ic3',
        'first_aid',
        'cpr',
        'employment_status',
        'work_schedule',
        'career_goals',
        'notes'
    ]


admin.site.register(CollegeInterest, CollegeInterestAdmin)
