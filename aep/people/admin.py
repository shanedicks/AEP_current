import requests
import bs4
from datetime import datetime, timedelta
from django.db import IntegrityError
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from import_export import resources, fields, widgets
from import_export.admin import ImportExportActionModelAdmin, ImportExportMixin
from .models import (
    Student, Staff, WIOA, PoP,
    CollegeInterest, Paperwork, Prospect, ProspectNote, full_merge
    )
from .tasks import send_to_state_task, possible_duplicate_report_task
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
            "title",
            "nickname",
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
            "ell_app",
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
            "title",
            "nickname",
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
            "student__ell_app",
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


class PaperworkResource(resources.ModelResource):

    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=widgets.ForeignKeyWidget(Student, 'WRU_ID')
    )

    class Meta:
        model = Paperwork
        fields = (
            "ferpa",
            "testing",
            "technology",
            "contract",
            "disclosure",
            "writing",
            "sd_reading",
            "sd_math",
            "sd_language",
            "sd_attention",
            "sd_other",
            "sh_self_se",
            "sh_resource_se",
            "sh_title1_read",
            "sh_title1_math",
            "sh_504",
            "sh_medication",
            "sh_other",
            "sh_request",
            "writing_sample",
            "signature",
            "guardian_signature",
            "sig_date",
            "g_sig_date",
            "pic_id",
            "pic_id_file",
            "eligibility_status",
            "eligibility_doc_type",
            "eligibility_doc",
            "eligibility_doc_expiration"
        )


class PopResource(resources.ModelResource):

    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=widgets.ForeignKeyWidget(Student, 'WRU_ID')
    )

    class Meta:
        model = PoP
        fields = (
            'id',
            'student',
            'start_date',
            'last_service_date',
            'active',
            'made_gain',
            'pretest_date',
            'pretest_type',
        )


class ProspectResource(resources.ModelResource):

    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=widgets.ForeignKeyWidget(Student, 'WRU_ID')
    )

    class Meta:
        model = Prospect
        fields = (
            'id',
            'student',
            'advisor',
            'advisor__last_name',
            'first_name',
            'last_name',
            'email',
            'phone',
            'dob',
            'contact_preference',
            'primary_language',
            'active',
            'registration_date',
            'duplicate',
            'for_credit',
            'slug'
        )


class ProspectNoteResource(resources.ModelResource):

    class Meta:
        model = ProspectNote
        fields = (
            'id',
            'prospect',
            'prospect__last_name',
            'prospect__first_name',
            'prospect__advisor__last_name',
            'contact_date',
            'contact_method',
            'successful',
            'notes'
        )


class PopAdmin(ImportExportActionModelAdmin):

    resource_class = PopResource

    search_fields = [
        'student__last_name',
        'student__first_name',
        'student__WRU_ID'
    ]

    list_display = (
        '__str__',
        'pretest_type',
        'pretest_date',
        'active',
        'made_gain',
    )

    fields = [
        ('start_date',
        'last_service_date'),
        ('active',
        'made_gain'),
        'pretest_date',
        'pretest_type'
    ]

    list_filter = [
        'active',
        'made_gain',
        'pretest_type',
        'pretest_date'
    ]

    list_editable = [
        "made_gain",
        "active"
    ]

admin.site.register(PoP, PopAdmin)

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
        'eligibility_verified'
    )

    list_editable = (
        'paperwork',
        'folder',
        'orientation',
        'eligibility_verified'
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
        'ell_app',
        'duplicate',
    )

    search_fields = [
        "first_name",
        "last_name",
        'phone',
        'email',
        'WRU_ID',
        'intake_date',
        'partner',
        'dob'
    ]

    fields = [
        ("WIOA",
         "tests"),
        "notes",
        'partner',
        ("WRU_ID",
         "slug"),
        'eligibility_verified',
        "intake_date",
        ("first_name",
         "last_name",
         "nickname"),
        "title",
        ("dob",
         "gender",
         "marital_status"),
        "US_citizen",
        ("email",
         "alt_email"),
        ("phone",
         "alt_phone"),
        ("street_address_1",
         "street_address_2"),
        ("city",
         "other_city"),
        ("state",
         "parish",
         "zip_code"),
        "emergency_contact",
        ("ec_phone",
         "ec_email",
         "ec_relation"),
        'primary_goal',
        "check_goal_1",
        "check_goal_2",
        "check_goal_3",
        "check_goal_4",
        "check_goal_5",
        "check_goal_6",
        "check_goal_7",
        "check_goal_8",
        "check_goal_9",
        ("ccr_app",
         "ell_app",
         "success_app",
         'e_learn_app',
         'accuplacer_app',
         'ell_online_app',
         'certifications_app'),
        ("online_cohort",
         "online_solo"),
        ("on_campus",
         "hybrid"),
        ("morning",
         "afternoon",
         "evening",
         "weekend"),
        ("mw",
         "tr",
         "sat"),
        "site_preference",
        ("computer_access",
         "internet_access"),
        ("duplicate",
         "duplicate_of"),
        "dupl_date",
        "prior_registration",
    ]

    readonly_fields = [
        "WIOA",
        "tests",
        "duplicate_of",
        "slug",
    ]

    actions = ImportExportActionModelAdmin.actions + (
        'testify',
        'create_elearn_record',
        'create_ace_record',
        'merge',
        'duplicate_report'
    )

    ordering = ['-id']

    def testify(self, request, queryset):
        for obj in queryset:
            obj.testify()

    def create_elearn_record(self, request, queryset):
        for obj in queryset:
            obj.create_elearn_record()

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
                    intake_year=timezone.now().year,
                    intake_semester=sem[str(timezone.now().month)]
                )

    def merge(self, request, queryset):
        q = queryset.order_by('pk')
        duplicate = q[1]
        orig = q[0]
        full_merge(orig, duplicate)

    def duplicate_report(self, request, queryset):
        id_list = [obj.id for obj in queryset]
        possible_duplicate_report_task.delay(request.user.email, id_list)

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
        'partner',
        'prospect_advisor'
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

    autocomplete_fields = [
        "user"
    ]


admin.site.register(Staff, StaffAdmin)


class PaperworkAdmin(ImportExportActionModelAdmin):

    resource_class = PaperworkResource

    list_display = (
        'student',
        'ferpa',
        'testing',
        'technology',
        'contract',
        'disclosure',
        'writing',
        'pic_id',
        'pic_id_file'
    )

    list_editable = (
        'ferpa',
        'testing',
        'technology',
        'contract',
        'disclosure',
        'writing',
        'pic_id'
    )

    search_fields = [
        'student__last_name',
        'student__first_name',
        'student__WRU_ID'
    ]

    fields = (
        "ferpa",
        "testing",
        "technology",
        "contract",
        "disclosure",
        "writing",
        "pic_id",
        "pic_id_file",
        "eligibility_status",
        "eligibility_doc_type",
        "eligibility_doc",
        "eligibility_verified_by",
        "eligibility_verified_at",
        "eligibility_doc_expiration",
        "sd_reading",
        "sd_math",
        "sd_language",
        "sd_attention",
        "sd_other",
        "sh_self_se",
        "sh_resource_se",
        "sh_title1_read",
        "sh_title1_math",
        "sh_504",
        "sh_medication",
        "sh_other",
        "sh_request",
        "signature",
        "guardian_signature",
        "sig_date",
        "g_sig_date"
    )

    readonly_fields = (
        "signature",
        "guardian_signature",
        "sig_date",
        "g_sig_date",
        "eligibility_verified_by",
        "eligibility_verified_at",
    )

admin.site.register(Paperwork, PaperworkAdmin)


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
            "student",
            "SID",
            (
                "hispanic_latino",
                "amer_indian",
                "asian",
                "black",
                "white",
                "pacific_islander"
            ),(
                "country",
                "other_country",
            ),(
                "native_language",
                "other_language"
            ),(
                "highest_level_completed",
                "highet_level_at_entry",
                "school_location"
            ),
            (
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
                "neurological_impairments"
            ),
            (
                "household_income",
                "household_size",
            ),(
                "current_employment_status",
                "employer",
                "occupation",
            ),(
                "current_industry",
                "industry_preference"
            ),
            "migrant_seasonal_status",
            "long_term_unemployed",
            "TANF",
            "TANF_2",
            "SNAP",
            "SSI",
            "Tstate",
            "veteran",
            "parental_status",
            "single_parent",
            "displaced_homemaker",
            "lacks_adequate_residence",
            "criminal_record",
            "foster_care",
            "help_with_schoolwork",
            "student_teacher_contact",
            "parent_volunteering",
            "read_to_children",
            "visit_library",
            "purchase_books",
            "referred_by",
            "digital_signature",
            "disability_notice",
            "request_accommodation",
    )

    readonly_fields = ["student"]

    actions = ImportExportActionModelAdmin.actions + (
        'check_for_state_id',
        'send_to_state',
        'verify',
        'full_send'
    )

    def get_AEP_ID(self, obj):
        return obj.student.AEP_ID
    get_AEP_ID.admin_order_field = "AEP_ID"
    get_AEP_ID.short_description = "AEP ID"

    def get_WRU_ID(self, obj):
        return obj.student.WRU_ID
    get_WRU_ID.admin_order_field = "student__WRU_ID"
    get_WRU_ID.short_description = "WRU ID"

    def check_for_state_id(self, request, queryset):
        wioa_id_list = [obj.id for obj in queryset]
        send_to_state_task.delay(wioa_id_list, 'check_for_state_id')

    def send_to_state(self, request, queryset):
        wioa_id_list = [obj.id for obj in queryset]
        send_to_state_task.delay(wioa_id_list, 'send_to_state')

    def verify(self, request, queryset):
        wioa_id_list = [obj.id for obj in queryset]
        send_to_state_task.delay(wioa_id_list, 'verify')

    def full_send(self, request, queryset):
        wioa_id_list = [obj.id for obj in queryset]
        send_to_state_task.delay(wioa_id_list, 'send')

admin.site.register(WIOA, WIOAAdmin)


class CustomUserAdmin(ImportExportMixin, UserAdmin):
    resource_class = UserResource

    list_display = ("username", "last_name", "first_name", "email")

    search_fields = [
        "username",
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

class ProspectAdmin(ImportExportActionModelAdmin):

    resource_class = ProspectResource

    search_fields = [
        'last_name',
        'first_name',
        'dob'
    ]

    ordering = [
        "-registration_date"
    ]

    list_display = [
        '__str__',
        'dob',
        'registration_date',
        'student',
        'advisor',
        'advisor_assigned_date',
        'active',
        'duplicate',
        'returning_student'
    ]

    list_filter = [
        'active',
        'registration_date',
        'advisor_assigned_date',
        ('advisor', admin.RelatedOnlyFieldListFilter)

    ]

    list_editable = [
        'active',
        'duplicate',
        'returning_student'
    ]

    fields = [
        'advisor',
        'first_name',
        'last_name',
        'email',
        'phone',
        'dob',
        'contact_preference',
        'primary_language',
        'active',
        'duplicate',
        'for_credit'
    ]



admin.site.register(Prospect, ProspectAdmin)


class ProspectNoteAdmin(ImportExportActionModelAdmin):

    resource_class = ProspectNoteResource

    list_display = [
        '__str__'
    ]

    fields = [
        'contact_date',
        'contact_method',
        'successful',
        'notes'       
    ]

admin.site.register(ProspectNote, ProspectNoteAdmin)
