from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from import_export import resources
from import_export.admin import ImportExportModelAdmin, ImportExportMixin
from .models import Student, Staff, WIOA

# Register your models here.
admin.site.register(Staff)


class UserResource(resources.ModelResource):

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email"
        )


class StudentResource(resources.ModelResource):

    class Meta:
        model = Student
        fields = (
            "id",
            "user__first_name",
            "user__last_name",
            "user__email",
            "dob",
            "AEP_ID",
            "WRU_ID",
            "gender",
            "marital_status",
            "US_citizen",
            "other_ID",
            "program",
            "prior_registration",
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
            "ec_relation"
        )


class WIOAResource(resources.ModelResource):

    class Meta:
        model = WIOA
        fields = (
            "id",
            "student__user__first_name",
            "student__user__last_name",
            "student__user__email",
            "student__AEP_ID",
            "student__WRU_ID",
            "student__dob",
            "student__gender",
            "student__marital_status",
            "student__US_citizen",
            "student__other_ID",
            "student__program",
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


class StudentAdmin(ImportExportModelAdmin):

    resource_class = StudentResource

    list_display = ("__str__", "AEP_ID", "WRU_ID", "dob")

    search_fields = ["user__first_name", "user__last_name", 'WRU_ID']

    fields = [
        "user",
        ("WRU_ID",
         "AEP_ID"),
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
        "state",
    ]


admin.site.register(Student, StudentAdmin)


class WIOAAdmin(ImportExportModelAdmin):
    resource_class = WIOAResource

    list_display = ("__str__", "get_AEP_ID", "get_WRU_ID")

    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "student__AEP_ID",
        "student__WRU_ID"
    ]

    def get_AEP_ID(self, obj):
        return obj.student.AEP_ID
    get_AEP_ID.admin_order_field = "AEP_ID"
    get_AEP_ID.short_description = "AEP ID"

    def get_WRU_ID(self, obj):
        return obj.student.WRU_ID
    get_WRU_ID.admin_order_field = "WRU_ID"
    get_WRU_ID.short_description = "WRU ID"


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
