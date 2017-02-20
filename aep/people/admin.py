import requests
import bs4
from datetime import datetime
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from import_export import resources, fields, widgets
from import_export.admin import ImportExportActionModelAdmin, ImportExportMixin
from .models import Student, Staff, WIOA, CollegeInterest
from assessments.models import TestHistory


admin.site.register(CollegeInterest)


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
            'user',
            "user__first_name",
            "user__last_name",
            "user__email",
            "dob",
            'intake_date',
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
            "user__first_name",
            "user__last_name",
            "user__email",
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
            "ec_relation"
        )


class WIOAResource(resources.ModelResource):

    class Meta:
        model = WIOA
        fields = (
            "id",
            "student__user__id",
            "student__id",
            "student__user__first_name",
            "student__user__last_name",
            "student__user__email",
            "student__AEP_ID",
            "student__WRU_ID",
            "student__dob",
            "student__intake_date",
            "student__gender",
            "student__marital_status",
            "student__US_citizen",
            "student__other_ID",
            "student__program",
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

    list_display = ("__str__", "WRU_ID", "dob", "intake_date")
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

    actions = ['testify']

    def testify(self, request, queryset):
        for obj in queryset:
            if TestHistory.objects.filter(student=obj).exists():
                continue
            else:
                TestHistory.objects.create(student=obj, student_wru=obj.WRU_ID)


admin.site.register(Student, StudentAdmin)


class StaffAdmin(ImportExportActionModelAdmin):
    resource_class = StaffResource

    list_display = ("__str__", "phone", "get_email")

    search_fields = [
        "user__first_name",
        "user__last_name",
    ]

    def get_email(self, obj):
        return obj.user.email
    get_email.admin_order_field = "Email"
    get_email.short_description = "Email"


admin.site.register(Staff, StaffAdmin)


def convert_date_format(date_string):
    date_input = datetime.strptime(date_string, "%m/%d/%y")
    return datetime.strftime(date_input, "%m/%d/%Y")


def get_SID(sid):
    return "".join(sid.split("-"))

def get_age_at_intake(dob, intake_date):
    diff = intake_date - dob
    age = diff.days // 365
    return age


def citizen(input):
    if input == 1:
        cit = "true"
    else:
        cit = "false"
    return cit


def marital(input):
    statuses = {
        "S": "1",
        "M": "2",
        "D": "3",
        "W": "4",
        "O": "5"
    }
    return statuses[input]


def gender(input):
    genders = {
        "M": "2",
        "F": "1"
    }
    return genders[input]


def state(input):
    states = {
        "AL": "2",
        "AK": "1",
        "AZ": "4",
        "AR": "3",
        "CA": "5",
        "CO": "6",
        "CT": "7",
        "DC": "8",
        "DE": "9",
        "FL": "10",
        "GA": "11",
        "HI": "12",
        "ID": "14",
        "IL": "15",
        "IN": "16",
        "IA": "13",
        "KS": "17",
        "KY": "18",
        "LA": "19",
        "ME": "22",
        "MA": "20",
        "MD": "21",
        "MI": "23",
        "MN": "24",
        "MS": "26",
        "MO": "25",
        "MT": "27",
        "NE": "30",
        "NV": "34",
        "NH": "31",
        "NJ": "32",
        "NM": "33",
        "NY": "35",
        "NC": "28",
        "ND": "29",
        "OH": "36",
        "OK": "37",
        "OR": "38",
        "PA": "39",
        "RI": "40",
        "SC": "41",
        "SD": "42",
        "TN": "43",
        "TX": "44",
        "UT": "45",
        "VA": "46",
        "VT": "47",
        "WA": "48",
        "WV": "50",
        "WI": "49",
        "WY": "51"
    }
    return states[input]


def email_status(input):
    if input != "":
        return "true"
    else:
        return "false"


def true_false(input):
    if input == "1":
        return "true"
    else:
        return "false"


def hl_tf(input):
    if input == "1":
        return "True"
    else:
        return "False"


def primary_program(input):
    programs = {
        "C": "1",
        "E": "7",
        "D": "12",
        "S": "14",
        "A": "2"
    }
    return programs[input]


def secondary_program(input):
    programs = {
        "C": "8",
        "E": "6",
        "D": "",
        "S": "",
        "A": ""
    }
    return programs[input]


def esl(input):
    if input == "E":
        return "true"
    else:
        return "false"


def employment_status(input):
    emp = {
        "1": "1_EM",
        "2": "3_UE",
        "3": "4_UNL",
        "4": "5_NLF",
        "5": "1_EM",
        "6": "5_NLF"
    }
    return emp[input]


class WIOAAdmin(ImportExportActionModelAdmin):
    resource_class = WIOAResource

    list_display = ("__str__", "get_AEP_ID", "get_WRU_ID")

    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "student__AEP_ID",
        "student__WRU_ID"
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

    actions =['send_to_state']

    def get_AEP_ID(self, obj):
        return obj.student.AEP_ID
    get_AEP_ID.admin_order_field = "AEP_ID"
    get_AEP_ID.short_description = "AEP ID"

    def get_WRU_ID(self, obj):
        return obj.student.WRU_ID
    get_WRU_ID.admin_order_field = "WRU_ID"
    get_WRU_ID.short_description = "WRU ID"

    def send_to_state(self, request, queryset):
        session = requests.Session()

        login = {
            'Provider': '9',
            'Parish': '19',
            'Login': 'shanedicks',
            'Password': 'LCTCS1617passDATA',
            'btnLogin': 'Login'
        }

        session.post('https://workreadyu.lctcs.edu/UserProfile/Login', data=login)

        for obj in queryset:

            student = {
                "hdnRoleType": "2",
                "EnrollPStat.IntakeDate": obj.student.intake_date,
                "FY": "4",
                "lblCurrentFY": "4",
                "FYBginDate": "7/1/2016",
                "FYEndDate": "6/30/2017",
                "hdnProviderId": "DELGADO COMMUNITY COLLEGE",
                "StudentId": "0",
                "SSN": get_SID(obj.SID),
                "LastName": obj.student.user.last_name,
                "FirstName": obj.student.user.first_name,
                "MiddleInitial": "",
                "DateOfBirth": obj.student.dob,
                "Age": get_age_at_intake(obj.student.dob, obj.student.intake_date),
                "USCitizen": citizen(obj.student.US_citizen),
                "MaritalStatusId": marital(obj.student.marital_status),
                "Gender": gender(obj.student.gender),
                "OtherID": "",
                "Suffix": "",
                "Address.Street1": obj.student.street_address_1,
                "Address.Street2": obj.student.street_address_2,
                "Address.City": obj.student.city,
                "Address.StateId": state(obj.student.state),
                "Address.Zip": obj.student.zip_code,
                "Address.AddressTypeId": "1",
                "Address.Status": "true",
                "Address.Status": "false",
                "Address.VTCountyId": obj.student.parish,
                "Telephone.PrimaryPhoneNumber": obj.student.phone,
                "Telephone.PrimaryPhoneTypeId": "3",
                "Telephone.PrimaryPhoneStatus": "true",
                "Telephone.PrimaryPhoneStatus": "false",
                "Telephone.AlternativePhoneNumber1": "",
                "Telephone.AlternativePhoneType1Id": "",
                "Telephone.AlternativePhoneStatus1": "false",
                "Telephone.AlternativePhoneNumber2": "",
                "Telephone.AlternativePhoneType2Id": "",
                "Telephone.AlternativePhoneStatus2": "false",
                "Telephone.AlternativePhoneNumber3": "",
                "Telephone.AlternativePhoneTypeId3": "",
                "Telephone.AlternativePhoneNumberStatus3": "false",
                "Emergency.LastName": "",
                "Emergency.FirstName": "",
                "Emergency.RelationshipId": "",
                "Emergency.Telephone1": "",
                "Emergency.Telephone2": "",
                "Email.Email1": obj.student.user.email,
                "Email.EmailTypeId": "1",
                "Email.EmailStatus": email_status(obj.student.user.email),
                "HispanicLatino": hl_tf(obj.hispanic_latino),
                "Ethnicity_1": true_false(obj.amer_indian),
                "Ethnicity_2": true_false(obj.asian),
                "Ethnicity_3": true_false(obj.black),
                "Ethnicity_5": true_false(obj.white),
                "Ethnicity_4": true_false(obj.pacific_islander),
                "Program.ProgramTypeId": primary_program(obj.student.program),
                "Program.StateKeyword": "",
                "Program.SecondaryProgram1TypeId": secondary_program(obj.student.program),
                "ESLStudent": esl(obj.student.program),
                "ESLStudent": "false",
                "Program.Keyword": "",
                "Program.SecondaryProgram2TypeId": "",
                "Program.NativeLanguage": obj.native_language,
                "Program.SecondaryProgram3TypeId": "",
                "Program.SecondaryProgram4TypeId": "",
                "Program.CountryOfHighestEducation": obj.country,
                "Program.PastEnrollment": true_false(obj.student.prior_registration),
                "Program.PastEnrollCollege": "",
                "EmploymentStatusId": employment_status(obj.current_employment_status),
                "EnrollPStat.EmploymentLocation": obj.employer,
                "EnrollPStat.Occupation": obj.occupation,
                "EnrollSStat.PublicAssistance": true_false(obj.recieves_public_assistance),
                "EnrollSStat.RuralArea": true_false(obj.rural_area),
                "EnrollSStat.LowIncome": true_false(obj.low_family_income),
                "EnrollSStat.DisplayedHomemaker": true_false(obj.displaced_homemaker),
                "EnrollSStat.SingleParent": true_false(obj.single_parent),
                "EnrollSStat.DislocatedWorker": true_false(obj.dislocated_worker),
                "Disability_12": true_false(obj.adhd),
                "Disability_13": true_false(obj.autism),
                "Disability_9": true_false(obj.deaf_blind),
                "Disability_3": true_false(obj.deaf),
                "Disability_6": true_false(obj.emotional_disturbance),
                "Disability_15": true_false(obj.k12_iep),
                "Disability_2": true_false(obj.hard_of_hearing),
                "Disability_1": true_false(obj.intellectual_disability),
                "Disability_10": true_false(obj.multiple_disabilities),
                "Disability_7": true_false(obj.orthopedic_impairment),
                "Disability_8": true_false(obj.other_health_impairment),
                "Disability_11": true_false(obj.learning_disability),
                "Disability_4": true_false(obj.speech_or_lang_impairment),
                "Disability_14": true_false(obj.traumatic_brain_injury),
                "Disability_5": true_false(obj.visual_impairment),
                "SpecLearningDisId": "11",
                "Dislearning_4": true_false(obj.dyscalculia),
                "Dislearning_3": true_false(obj.dysgraphia),
                "Dislearning_2": true_false(obj.dyslexia),
                "Dislearning_1": true_false(obj.neurological_impairments),
                "HighestId": obj.highest_level_completed,
                "HighLocId": obj.school_location,
                "GoalId": "",
                "ReferralDate": "",
                "ReferralTo": "",
                "CommentDate": "",
                "Comment": "",
                "btnSave": "Create"
            }

            session.post('https://workreadyu.lctcs.edu/Student/Create/CreateLink', data=student)

            search = {
                'LastNameTextBox': obj.student.user.last_name,
                'FirstNameTextBox': obj.student.user.first_name,
                'btnFilter': 'Filter List'
            }

            s = session.get('https://workreadyu.lctcs.edu/Student', data=search)

            soup = bs4.BeautifulSoup(s.text, "html.parser")

            wru = soup.select("table.Webgrid > tbody > tr > td")[9].text.encode('utf-8')

            obj.student.WRU_ID = wru
            obj.student.save()


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
