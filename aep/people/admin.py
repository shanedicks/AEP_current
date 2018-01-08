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
            "first_name",
            "last_name",
            "email",
            "dob",
            'intake_date',
            "AEP_ID",
            "WRU_ID",
            "gender",
            "marital_status",
            "US_citizen",
            "other_ID",
            "ccr_app",
            "esl_app",
            "e_learn_app",
            "ace_app",
            "success_app",
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
            "first_name",
            "last_name",
            "email",
            'teacher',
            'coach',
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
        'ccr_app',
        'esl_app',
        'ace_app',
        'e_learn_app',
        'success_app',
        'accuplacer_app'
    )

    list_filter = (
        'ccr_app',
        'esl_app',
        'ace_app',
        'e_learn_app',
        'success_app',
        'accuplacer_app'
    )

    search_fields = [
        "first_name",
        "last_name",
        'email',
        'WRU_ID',
        'intake_date',
    ]

    fields = [
        "user",
        "first_name",
        "last_name",
        "email",
        ("WRU_ID",
         'program'),
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

    actions = [
        'testify',
        'create_elearn_record',
        'full_merge'
    ]

    ordering = ['-id']

    def testify(self, request, queryset):
        for obj in queryset:
            if TestHistory.objects.filter(student=obj).exists():
                continue
            else:
                TestHistory.objects.create(student=obj, student_wru=obj.WRU_ID)

    def create_elearn_record(self, request, queryset):
        for obj in queryset:
            if ElearnRecord.objects.filter(student=obj).exists():
                continue
            else:
                ElearnRecord.objects.create(
                    student=obj,
                    intake_date=datetime.today()
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
                q[1].tests.delete()
                t.save()
        except ObjectDoesNotExist:
            pass


    def move_classes(self, request, queryset):
        q = queryset.order_by('pk')
        for c in q[0].classes.all():
            c.student = q[1]
            c.save()

    def move_appointments(self, request, queryset):
        q = queryset.order_by('pk')
        for a in q[0].test_appointments.all():
            a.student = q[1]
            try:
                a.save()
            except IntegrityError:
                pass

    def move_elearn_record(self, request, queryset):
        q = queryset.order_by('pk')
        try:
            e = q[0].elearn_record
            e.student = q[1]
            e.save()
        except ObjectDoesNotExist:
            pass

    def move_coaching(self, request, queryset):
        q = queryset.order_by('pk')
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

    def move_ace_record(self, request, queryset):
        q = queryset.order_by('pk')
        try:
            a = q[0].ace_record
            a.student = q[1]
            a.save()
        except ObjectDoesNotExist:
            pass

    def full_merge(self, request, queryset):
        self.move_test_history(request, queryset)
        self.move_classes(request, queryset)
        self.move_appointments(request, queryset)
        self.move_elearn_record(request, queryset)
        self.move_coaching(request, queryset)
        self.move_ace_record(request, queryset)


admin.site.register(Student, StudentAdmin)


class StaffAdmin(ImportExportActionModelAdmin):
    resource_class = StaffResource

    list_display = (
        "user",
        "__str__",
        "wru",
        "phone",
        "get_email",
        "g_suite_email",
        'teacher',
        'coach'
    )

    list_filter = (
        'active',
        'teacher',
        'coach'
    )

    search_fields = [
        "first_name",
        "last_name",
    ]

    def get_email(self, obj):
        return obj.email
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
    if input is True:
        return "true"
    else:
        return "false"


def hl_tf(input):
    if input is True:
        return "True"
    else:
        return "False"


def primary_program(student):
    program = "1"
    if student.esl_app:
        program = '7'
    elif student.e_learn_app:
        program = '12'
    elif student.ace_app:
        program = '2'
    elif student.success_app:
        program = '14'
    return program


def secondary_program(student):
    program = ""
    if student.ccr_app:
        program = '8'
    if student.esl_app:
        program = '6'
    return program


def esl(student):
    if student.esl_app:
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


def migrant(input):
    mig = {
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 0,
    }
    return mig[input]


def one_stop(input):
    o = {
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 0
    }
    return o[input]


def y_n_u(input):
    y = {
        "": 9,
        "1": 1,
        "2": 0,
        "3": 9
    }
    return y[input]


def school_status(input):
    status = {
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6
    }
    return status[input]


def dislocated(input):
    if input is True:
        return 1
    else:
        return 0


def voc_rehab(input):
    v = {
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 0
    }
    return v[input]


def wru_search(session, search_dict):
    s = session.get(
        'https://workreadyu.lctcs.edu/Student',
        data=search_dict
    )
    p = bs4.BeautifulSoup(
        s.text,
        "html.parser"
    )
    try:
        return p.select("table.Webgrid > tbody > tr > td")[9].text.encode('utf-8')
    except IndexError:
        return 'No ID'


class WIOAAdmin(ImportExportActionModelAdmin):

    resource_class = WIOAResource

    list_display = ("__str__", "get_WRU_ID")

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

    actions = ['send_to_state', 'check_for_state_id']

    def get_AEP_ID(self, obj):
        return obj.student.AEP_ID
    get_AEP_ID.admin_order_field = "AEP_ID"
    get_AEP_ID.short_description = "AEP ID"

    def get_WRU_ID(self, obj):
        return obj.student.WRU_ID
    get_WRU_ID.admin_order_field = "WRU_ID"
    get_WRU_ID.short_description = "WRU ID"

    def check_for_state_id(self, request, queryset):
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

            search = {
                'LastNameTextBox': obj.student.last_name,
                'FirstNameTextBox': obj.student.first_name,
                'Status': -1,
                'AgeSearchType': 1,
                'AgeFromInequality': 4,
                'AgeFromTextBox': get_age_at_intake(obj.student.dob, obj.student.intake_date),
                'btnFilter': 'Filter List'
            }

            wru = wru_search(session, search)

            if wru == 'No ID':
                if obj.SID:
                    search = {
                        'SSNTextBox': get_SID(obj.SID),
                        'Status': -1,
                        'btnFilter': 'Filter List'
                    }
                    wru = wru_search(session, search)

            if wru != 'No ID':
                wru = b'x' + wru

            obj.student.WRU_ID = wru
            obj.student.save()

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
                "hdnInactiveStateKey": ",2,3,4,5,",
                "hdnInactiveProg": ",7,13,",
                "hdnInactiveEmpStat": ",4_UNL, 5_NLF,",
                "EnrollPStat.IntakeDate": obj.student.intake_date,
                "FY": "5",
                "lblCurrentFY": "5",
                "FYBginDate": "7/1/2017",
                "FYEndDate": "6/30/2018",
                "hdnProviderId": "DELGADO COMMUNITY COLLEGE",
                "StudentId": "0",
                "SSN": get_SID(obj.SID),
                "LastName": obj.student.last_name,
                "FirstName": obj.student.first_name,
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
                "Email.Email1": obj.student.email,
                "Email.EmailTypeId": "1",
                "Email.EmailStatus": email_status(obj.student.email),
                "HispanicLatino": hl_tf(obj.hispanic_latino),
                "Ethnicity_1": true_false(obj.amer_indian),
                "Ethnicity_2": true_false(obj.asian),
                "Ethnicity_3": true_false(obj.black),
                "Ethnicity_5": true_false(obj.white),
                "Ethnicity_4": true_false(obj.pacific_islander),
                "Program.ProgramTypeId": primary_program(obj.student),
                "Program.StateKeyword": "",
                "Program.SecondaryProgram1TypeId": secondary_program(obj.student),
                "ESLStudent": esl(obj.student),
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
                "StudentWIOADetail.MigrantAndSeasonalFarmworker": migrant(obj.migrant_seasonal_status),
                "StudentWIOADetail.NNLongTermUnemployed": true_false(obj.long_term_unemployed),
                "StudentWIOADetail.DislocatedWorker": dislocated(obj.dislocated_worker),
                "StudentWIOADetail.NNCulturalBarriers": true_false(obj.cult_barriers_hind_emp),
                "StudentWIOADetail.NNFostercareYouth": true_false(obj.in_foster_care),
                "StudentWIOADetail.NNAgedOutFosterCare": true_false(obj.aged_out_foster_care),
                "StudentWIOADetail.NNExhaustingTANFWithin2Years": true_false(obj.exhaust_tanf),
                "StudentWIOADetail.IndividualWithDisability": "",
                "StudentWIOADetail.JobCorps": y_n_u(obj.job_corps),
                "StudentWIOADetail.YouthBuild": y_n_u(obj.youth_build),
                "StudentWIOADetail.NNLowLevelsOfLiteracy": "false",
                "StudentWIOADetail.NNRecievedAssistance": true_false(obj.recieves_public_assistance),
                "StudentWIOADetail.NNIncomeBelowStandardIncomeLevel": true_false(obj.low_family_income),
                "StudentWIOADetail.NNReceiveReducedPriceLunch": "false",
                "StudentWIOADetail.NNLowIncomeFosterChild": true_false(obj.state_payed_foster),
                "StudentWIOADetail.NNLowIncomeIndividualWithDisability": true_false(obj.disabled_in_poverty),
                "StudentWIOADetail.NNHomelessOrRunawayYouth": true_false(obj.runaway_youth),
                "StudentWIOADetail.NNLivingInHighPovertyArea": true_false(obj.youth_in_high_poverty_area),
                "StudentWIOADetail.NNSubjectToCriminalJusticeProcess": true_false(obj.subject_of_criminal_justice),
                "StudentWIOADetail.NNBarriersToEmployment": true_false(obj.arrest_record_employment_barrier),
                "StudentWIOADetail.NNLacksFixedNighttimeResidence": true_false(obj.lacks_adequate_residence),
                "StudentWIOADetail.NNNighttimeResidenceNotForHumans": true_false(obj.irregular_sleep_accomodation),
                "StudentWIOADetail.NNMigratoryChild": true_false(obj.migratory_child),
                "StudentWIOADetail.NNBelow18AndAbsetFromHome": true_false(obj.runaway_youth),
                "StudentWIOADetail.Adult": one_stop(obj.adult_one_stop),
                "StudentWIOADetail.AdultDateofLastService": "",
                "StudentWIOADetail.AdultProviderName": "",
                "StudentWIOADetail.AdultTypeOfService": 0,
                "StudentWIOADetail.Youth": one_stop(obj.youth_one_stop),
                "StudentWIOADetail.YouthDateofLastService": "",
                "StudentWIOADetail.YouthProviderName": "",
                "StudentWIOADetail.YouthTypeOfService": 0,
                "StudentWIOADetail.VocationalRehabilitation": voc_rehab(obj.voc_rehab),
                "StudentWIOADetail.WagnerPeyserAct": y_n_u(obj.wagner_peyser),
                "StudentWIOADetail.SchoolStatusAtParticipation": school_status(obj.school_status),
                "StudentWIOADetail.ReceivedTraining": "",
                "StudentWIOADetail.EligibleTrainingProvider": "",
                "StudentWIOADetail.TypeTrainingServices": "",
                "StudentWIOADetail.EligibleTrainingProviderStudy": "",
                "StudentWIOADetail.EligibleTrainingProviderCIP": "",
                "StudentWIOADetail.TypeTrainingService2": "",
                "StudentWIOADetail.TypeTrainingService3": "",
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

            session.post(
                'https://workreadyu.lctcs.edu/Student/CreateWithWIOA/CreateLink',
                data=student
            )

            search = {
                'LastNameTextBox': obj.student.last_name,
                'FirstNameTextBox': obj.student.first_name,
                'FromTextBox': obj.student.intake_date,
                'ToTextBox': obj.student.intake_date,
                'btnFilter': 'Filter List'
            }

            wru = wru_search(session, search)

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
