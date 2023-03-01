from apiclient import discovery
from httplib2 import Http
from datetime import datetime
from django.contrib import admin
from django.conf import settings

from import_export import resources, fields, widgets
from import_export.admin import ImportExportActionModelAdmin
from oauth2client.service_account import ServiceAccountCredentials

from core.tasks import send_mail_task
from people.models import Student, Staff
from .models import AceRecord, Coaching, Profile, MeetingNote, ElearnRecord
from .tasks import elearn_status_task, create_g_suite_accounts_task



class AceRecordResource(resources.ModelResource):

    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=widgets.ForeignKeyWidget(Student, 'WRU_ID')
    )

    class Meta:
        model = AceRecord
        fields = (
            'id',
            'student',
            'student__last_name',
            'student__first_name',
            'lola',
            'dcc_email',
            'ace_pathway',
            'program',
            'ace_status',
            'status_updated',
            'intake_semester',
            'intake_year',
            'hsd',
            'hsd_date',
            'media_release',
            'third_party_release',
            'read_072',
            'eng_062',
            'math_092',
            'math_098'
        )


class ElearnRecordResource(resources.ModelResource):

    student = fields.Field(
        column_name='student',
        attribute='student',
        widget=widgets.ForeignKeyWidget(Student, 'WRU_ID')
    )

    class Meta:
        model = ElearnRecord
        fields = (
            'id',
            'student',
            'student__last_name',
            'student__first_name',
            'elearn_status',
            'status_updated',
            'g_suite_email',
            'intake_date',
            'student__partner'
        )


class CoachingResource(resources.ModelResource):

    coachee = fields.Field(
        column_name='coachee',
        attribute='coachee',
        widget=widgets.ForeignKeyWidget(Student, 'WRU_ID')
    )

    coach = fields.Field(
        column_name='coach',
        attribute='coach',
        widget=widgets.ForeignKeyWidget(Staff, 'wru'))

    class Meta:
        model = Coaching
        fields = (
            'id',
            'coach',
            'coach__last_name',
            'coach__first_name',
            'coachee',
            'coachee__last_name',
            'coachee__first_name',
            'coaching_type',
            'active',
            'status',
            'start_date',
            'end_date',
        )

        export_order = fields


class ProfileResource(resources.ModelResource):

    class Meta:
        model = Profile
        fields = (
            'id',
            'student__WRU_ID',
            'student__last_name',
            'student__first_name',
            'health_pathway_interest',
            'crafts_pathway_interest',
            'it_pathway_interest',
            'hospitality_pathway_interest',
            'texts_ok',
            'smartphone',
            'webcam',
            'device',
            'contact_preference',
            'other_contact',
            'availability',
            'other_availability',
            'library',
            'instagram',
            'twitter',
            'facebook',
            'linkedin',
            'grade_level',
            'school_experience',
            'special_help',
            'special_help_desc',
            'conditions',
            'elearn_experience',
            'math',
            'english',
            'social_studies',
            'best_classes',
            'worst_classes',
            'favorite_subject',
            'completion_time',
            'hours_per_week',
            'personal_goal',
            'frustrated',
            'anything_else'
        )

class MeetingNoteResource(resources.ModelResource):

    class Meta:
        model = MeetingNote
        fields = (
            'id',
            'coaching',
            'coaching__coach__last_name',
            'coaching__coachee__last_name',
            'coaching__coachee__first_name',
            'coaching__coachee__WRU_ID',
            'meeting_type',
            'meeting_date',
            'start_time',
            'end_time',
            'progress',
            'next_steps',
            'notes'
        )


class AceRecordAdmin(ImportExportActionModelAdmin):

    resource_class = AceRecordResource

    list_display = (
        'student',
        'ace_status_column',
        'intake_column',
        'lola',
        'dcc_email',
        'ace_pathway',
        'program',
        'hsd_column',
        'media_release',
        'third_party_release'
    )

    search_fields = [
        'student__last_name',
        'student__first_name',
        'student__WRU_ID'
    ]

    fields = [
        'student',
        'ace_status',
        'status_updated',
        'intake_semester',
        'intake_year',
        'lola',
        'dcc_email',
        'ace_pathway',
        'program',
        'hsd',
        'hsd_date',
        'media_release',
        'third_party_release',
        'read_072',
        'eng_062',
        'math_092',
        'math_098'
    ]

    readonly_fields = ['student']

    def ace_status_column(self, obj):
        return("%s as of %s" % (obj.ace_status, obj.status_updated))
    ace_status_column.short_description = 'ACE Status'

    def intake_column(self, obj):
        return("%s %s" % (obj.intake_semester, obj.intake_year))
    intake_column.short_description = 'Intake'

    def hsd_column(self, obj):
        if obj.hsd_date is not None:
            date = obj.hsd_date.strftime("%a, %b %d")
        else:
            date = 'N/A'
        return("%s | %s" % (obj.hsd, date))
    hsd_column.short_description = "HSD/HSE | Date"


admin.site.register(AceRecord, AceRecordAdmin)


class ElearnRecordAdmin(ImportExportActionModelAdmin):

    resource_class = ElearnRecordResource

    list_display = (
        'student',
        'elearn_status',
        'status_updated',
        'intake_date',
        'g_suite_email'
    )

    list_filter = (
        'elearn_status',
    )

    search_fields = [
        'student__last_name',
        'student__first_name',
        'student__WRU_ID',
        'g_suite_email'
    ]

    fields = [
        'student',
        'elearn_status',
        'status_updated',
        'intake_date',
        'g_suite_email'
    ]

    readonly_fields = ['student']

    actions = ImportExportActionModelAdmin.actions + (
        'DLA_email', 
        'create_g_suite_account',
        'send_g_suite_info'
    )

    def DLA_email(self, request, queryset):
        for obj in queryset:
            if obj.elearn_status == 'Applicant':
                send_mail_task.delay(
                    subject="Application recieved for Delgado eLearn",
                    message="",
                    html_message="<p>Good Morning, eLearn Applicants!</p>"
                    "<p>This email is to confirm that your "
                    "application to eLearn <strong>has been received.</strong></p>"
                    "<h3><strong>What is eLearn?</h3>"
                    "<p>The eLearn Program is here to help you study to earn a "
                    "high school equivalency diploma (HiSET, formerly the GED), "
                    "and transition to college and career pathways.</p>"
                    "<h3>Why online learning?</h3>"
                    "<p>The internet is simply amazing! In 2017, online learning"
                    " has never been easier or more exciting! In eLearn, students"
                    " and teachers explore the web to find tools to learn, to grow"
                    ", and to reach our academic, professional, and personal goals!</p>"
                    "<h3>How to Finish Applying to eLearn</h3>"
                    "<p>This link below includes instructions on how to complete"
                    " the 2nd part of the application process. It is <strong>due by 9pm on"
                    " Wednesday, August 30th.</strong> This next step will take about 1 "
                    "hour to complete, so be sure to find time to get online!</p>"
                    "<p>Remember - the eLearn Program is popular and space is "
                    "limited, so we cannot guarantee that everyone will be "
                    "accepted. To improve your chances, <strong>be sure to "
                    "follow the instructions on the following website.</strong>"
                    "<p><a href='https://sites.google.com/site/applyingtoelearn/home'>"
                    "Click here to get started with the 2nd stage of "
                    "the eLearn application process.</a></p>"
                    "<p>Remember, this next stage is due by 9pm on Wednesday, August 30th."
                    "<p>Good luck, and we look forward to working with you soon!</p>"
                    "<p>Sincerely,</p>"
                    "<p>The eLearn Team</p>"
                    "<p>apply@elearnclass.org</p>",
                    from_email="noreply@elearnclass.org",
                    recipient_list=[obj.student.email],
                )
                elearn_status_task.delay(obj.id)

    def create_g_suite_account(self, request, queryset):
        id_list = [obj.id for obj in queryset]
        create_g_suite_accounts_task.delay(id_list)
        

    def send_g_suite_info(self, request, queryset):
        for obj in queryset:
            obj.send_g_suite_info()


admin.site.register(ElearnRecord, ElearnRecordAdmin)


class CoachingAdmin(ImportExportActionModelAdmin):

    resource_class = CoachingResource

    list_display = (
        '__str__',
        'coaching_type',
        'status',
        'active',
        'start_date',
        'end_date',
    )

    list_filter = (
        'coaching_type',
        'status',
        'active'
    )

    list_editable = (
        'status',
    )

    search_fields = [
        'coachee__last_name',
        'coachee__first_name',
        'coachee__WRU_ID',
        'coach__first_name',
        'coach__last_name'
    ]

    fields = [
        'coachee',
        'coach',
        'coaching_type',
        'status',
        'active',
        'start_date',
        'end_date',
    ]

    readonly_fields = (
        'coachee',
        'coach'
    )

    actions = ImportExportActionModelAdmin.actions + (
        'merge',
    )

    def merge(self, request, queryset):
        q = queryset.order_by('pk')
        n = q[1]
        o = q[0]
        if n.coaching_type == o.coaching_type and n.coach == o.coach:
            n.start_date = min(o.start_date, n.start_date)
            o.notes.update(coaching=n)
            o.active=False
            o.save()
            n.save()

admin.site.register(Coaching, CoachingAdmin)


class ProfileAdmin(ImportExportActionModelAdmin):

    resource_class = ProfileResource

    list_display = (
        '__str__',
    )

    search_fields = [
        'student__last_name',
        'student__first_name',
        'student__WRU_ID'
    ]

    fields = [
        'student',
        'health_pathway_interest',
        'crafts_pathway_interest',
        'it_pathway_interest',
        'hospitality_pathway_interest',
        'texts_ok',
        'smartphone',
        'webcam',
        'device',
        'contact_preference',
        'other_contact',
        'availability',
        'other_availability',
        'library',
        'instagram',
        'twitter',
        'facebook',
        'linkedin',
        'grade_level',
        'school_experience',
        'special_help',
        'special_help_desc',
        'conditions',
        'elearn_experience',
        'math',
        'english',
        'social_studies',
        'best_classes',
        'worst_classes',
        'favorite_subject',
        'completion_time',
        'hours_per_week',
        'personal_goal',
        'frustrated',
        'anything_else'
    ]

    readonly_fields = ['student']


admin.site.register(Profile, ProfileAdmin)


class MeetingNoteAdmin(ImportExportActionModelAdmin):

    resource_class = MeetingNoteResource

    list_display = (
        'coaching',
        'meeting_date',
        'start_time'
    )

    list_filter = (
        'meeting_date',
        'meeting_type'
    )

    search_fields = [
        'coaching__coachee__last_name',
        'coaching__coachee__first_name',
        'coaching__coachee__WRU_ID',
        'coaching__coach__last_name',
        'coaching__coach__first_name',
    ]

    fields = [
        'meeting_type',
        'student_no_show',
        'meeting_date',
        'start_time',
        'end_time',
        'meeting_topic',
        'progress',
        'next_steps',
        'notes'
    ]


admin.site.register(MeetingNote, MeetingNoteAdmin)
