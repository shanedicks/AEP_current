import requests
import bs4
from datetime import datetime, timedelta
from django.db import IntegrityError
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ObjectDoesNotExist
from import_export import resources, fields, widgets
from import_export.admin import ImportExportActionModelAdmin, ImportExportMixin
from .models import (
    Student, Staff, WIOA, PoP,
    CollegeInterest, Paperwork, Prospect, ProspectNote
    )
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
            "pronoun",
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
            "pronoun",
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
            'id',
            'student',
            'ferpa',
            'test_and_comp',
            'contract',
            'disclosure',
            'lsi',
            'writing',
            'pic_id'
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
        "notes",
        "first_name",
        "last_name",
        "title",
        "nickname",
        "pronoun",
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
        'full_merge',
    ]

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

    def move_test_history(self, request, q):
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
                clas_e_loc = q[1].tests.clas_e_loc_tests.all()
                clas_e_loc.update(student=t)
                gain = q[1].tests.gain_tests.all()
                gain.update(student=t)
                hiset = q[1].tests.hiset_practice_tests.all()
                hiset.update(student=t)
                if t.last_test_date == None:
                    t.last_test_date = q[1].tests.last_test_date
                q[1].tests.delete()
                t.save()
        except ObjectDoesNotExist:
            pass

    def move_classes(self, request, q):
        for c in q[0].classes.all():
            c.student = q[1]
            try:
                c.save()
            except IntegrityError:
                pass

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

    def copy_office_tracking(self, request, q):
        n = q[1]
        if n.paperwork != 'C' and q[0].paperwork != 'P':
            n.paperwork = q[0].paperwork
        if n.folder != 'C' and q[0].folder != 'P':
            n.folder = q[0].folder
        if n.orientation != 'C' and q[0].orientation != 'P':   
            n.orientation = q[0].orientation
        n.save()

    def move_or_copy_paperwork(self, request, q):
        try:
            p = q[0].student_paperwork
            p.student = q[1]
            try:
                p.save()
            except IntegrityError:
                np = q[1].student_paperwork
                np.ferpa = max(p.ferpa, np.ferpa)
                np.test_and_comp = max(p.test_and_comp , np.test_and_comp)
                np.contract = max(p.contract , np.contract)
                np.disclosure = max(p.disclosure , np.disclosure)
                np.lsi = max(p.lsi , np.lsi)
                np.writing = max(p.writing , np.writing)
                np.pic_id = max(p.pic_id , np.pic_id)
                np.save()
        except ObjectDoesNotExist:
            pass

    def merge_pops(self, pop, pop2):
            pop2.last_service_date = max(pop.last_service_date, pop2.last_service_date)
            pop2.active = max(pop.active, pop2.active)
            pop2.made_gain = max(pop.made_gain, pop2.made_gain)
            if pop2.pretest_date is not None and pop.pretest_date is not None:
                pop2.pretest_date = min(pop.pretest_date, pop2.pretest_date)
            elif pop.pretest_date is not None:
                pop2.pretest_date = pop.pretest_date
            pop2.pretest_type = max(pop.pretest_type, pop2.pretest_type)
            pop2.save()
            pop.delete()

    def move_or_merge_pops(self, request, q):
        og_pops = q[0].pop.all()
        for pop in og_pops:
            try:
                pop.student = q[1]
                pop.save()
            except IntegrityError:
                conflict = q[1].pop.get(
                    start_date=pop.start_date
                )
                self.merge_pops(pop, conflict)

        new_pops = q[1].pop.all()
        i, j = 0, 1
        while j < new_pops.count():
            older = new_pops[i]
            newer = new_pops[j]
            exit = older.last_service_date + timedelta(days=90)
            if newer.start_date <= exit:
                self.merge_pops(newer, older)
            i += 1
            j += 1

    def move_skill_masteries(self, request, q):
        sm = q[0].skillmasterys.all()
        for record in sm:
            try:
                record.student = q[1]
                record.save()
            except IntegrityError:
                pass              
                
    def move_certificates(self, request, q):
        c = q[0].certificates.all()
        for record in c:
            try:
                record.student = q[1]
                record.save()
            except IntegrityError:
                pass

    def move_course_completions(self, request, q):
        cc = q[0].coursecompletions.all()
        for record in cc:
            try:
                record.student = q[1]
                record.save()
            except IntegrityError:
                pass

    def move_prospects(self,request, q):
        p = q[0].prospects.all()
        for record in p:
            try:
                record.student = q[1]
                record.save()
            except IntegrityError:
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
        self.copy_office_tracking(request, q)
        self.move_or_copy_paperwork(request, q)
        self.move_or_merge_pops(request, q)
        self.move_skill_masteries(request, q)
        self.move_certificates(request, q)
        self.move_course_completions(request, q)
        self.move_prospects(request, q)
        n = q[1]
        o = q[0]
        n.intake_date = o.intake_date
        n.notes = o.notes
        nid = n.WRU_ID
        n.WRU_ID = o.WRU_ID
        n.save()
        if nid is None:
            o.WRU_ID = 'd' + o.WRU_ID
        else:
            o.WRU_ID = 'd' + nid.replace('x', '')
        o.duplicate_of = n
        o.duplicate = True
        o.dupl_date = timezone.now().date()
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


admin.site.register(Staff, StaffAdmin)


class PaperworkAdmin(ImportExportActionModelAdmin):

    resource_class = PaperworkResource

    list_display = (
        'student',
        'ferpa',
        'test_and_comp',
        'contract',
        'disclosure',
        'lsi',
        'writing',
        'pic_id'
    )

    list_editable = (
        'ferpa',
        'test_and_comp',
        'contract',
        'disclosure',
        'lsi',
        'writing',
        'pic_id'
    )

    search_fields = [
        'student__last_name',
        'student__first_name',
        'student__WRU_ID'
    ]

    fields = (
        'ferpa',
        'test_and_comp',
        'contract',
        'disclosure',
        'lsi',
        'writing',
        'pic_id'  
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

    actions = ImportExportActionModelAdmin.actions + ['send_to_state', 'check_for_state_id', 'verify']

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

    def verify(self, request, queryset):
        session = state_session()
        for obj in queryset:
            obj.verify(session)

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
