from apiclient import discovery
from httplib2 import Http
from datetime import datetime
from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings

from import_export import resources, fields, widgets
from import_export.admin import ImportExportActionModelAdmin
from oauth2client.service_account import ServiceAccountCredentials

from .models import AceRecord, Coaching, Profile, MeetingNote, ElearnRecord
from people.models import Student, Staff


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
            'student__user__last_name',
            'student__user__first_name',
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
            'third_party_release'
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
            'student__user__last_name',
            'student__user__first_name',
            'student__user__email',
            'student__phone',
            'elearn_status',
            'status_updated',
            'g_suite_email',
            'intake_date',
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
            'coach__user__last_name',
            'coach__user__first_name',
            'coachee',
            'coachee__user__last_name',
            'coachee__user__first_name',
            'coaching_type',
            'active',
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
            'student__user__last_name',
            'student__user__first_name',
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
            'coaching__coach',
            'coaching__coachee',
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
        'student__user__last_name',
        'student__user__first_name',
        'student__WRU_ID'
    ]

    fields = [
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
        'third_party_release'
    ]

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
        'student__user__last_name',
        'student__user__first_name',
        'student__WRU_ID'
    ]

    fields = [
        'elearn_status',
        'status_updated',
        'intake_date',
    ]

    actions = ['DLA_email', 'create_g_suite_account']

    def DLA_email(self, request, queryset):
        for obj in queryset:
            if obj.elearn_status == 'Applicant':
                send_mail(
                    "Application recieved for Delgado eLearn",
                    message="",
                    html_message="<h3>What's next?</h3><p>Please note that "
                    "eLearn is a bit different than taking classes on campus."
                    " In order to join the online program, there are a few "
                    "more steps you'll need to complete to finish your "
                    "application to eLearn in Adult Education at Delgado.</p>"
                    "<p>We are growing quickly and we hope to welcome all "
                    "students. But the program is popular and we therefore "
                    "can't guarantee that everyone will be accepted. So take "
                    "your time reading this page so you understand what to "
                    "expect next.</p><h3>The eLearn application process</h3>"
                    "<p>There are 3 parts to applying to eLearn:</p>"
                    "<ol><li><p><strong>Apply online</strong> - This is the "
                    "form that you've already submitted including your name "
                    "and contact information.</p></li><li><p><strong>Submit "
                    "digital literacy tests</strong> - The second step is to"
                    " take a few digital literacy tests. Since the eLearn "
                    "classes will be taken entirely online, it's important "
                    "that you have the basic computer skills needed to "
                    "succeed with online learning.</p><p>These digital "
                    "literacy tests will be emailed to you on Friday, "
                    "February 2nd. So check your inbox then. We will send the"
                    " email to the same address you used during the online "
                    "application.</p><p>Then, follow the directions in the "
                    "email to complete the second stage of the application "
                    "process.</p></li><li><p><strong>Check your inbox</strong>"
                    "- On Friday, February 2nd, we will email all students "
                    "with the status of the application. Your status could be:"
                    "</p><p><ul class='large-offset-3'><li><strong>Accepted"
                    "</strong> - If you are accepted, we will send you a link "
                    "to sign-up for an Orientation session at our City Park "
                    "Campus.</li><li><strong>On Hold</strong> - If we receive "
                    "a large amount of applications, you may be placed on hold"
                    " until we can schedule more Orientation sessions.</li>"
                    "<li><strong>Not Accepted</strong> - If you aren't "
                    "accepted, we will email you with an explanation why and "
                    "other options you still have for starting classes soon! If"
                    " you aren't accepted, that's okay! You can always apply "
                    "again during the next application period.</li></ul></p>"
                    "</li></ol><p>The best thing to do for now is re-read this "
                    "page to make sure you understand the full eLearn application"
                    " process, and then check your inbox for more instructions"
                    " coming soon!</p><h3>What if I want to start classes now?"
                    "</h3><p>That's great! We are excited to hear that you are"
                    " interested in starting school as soon as possible. If you"
                    " want to take classes this fall, you can consider enrolling"
                    " in classes on-campus. We offer morning, afternoon, and"
                    " evening classes at all campuses around the city, so we "
                    "suggest you start on-campus now and then consider "
                    "transitioning to online classes when we welcome more "
                    "students in early 2018.</p><p>"
                    "<a href='http://www.dcc.edu/academics/adult-ed/default.aspx'>"
                    "Click here</a> to learn more about taking classes on campus!"
                    "</p><p>And to learn more about eLearn and the application "
                    "process, <a href='https://www.youtube.com/watch?v=OKV3vymssSA'>"
                    "check out this video!</a></p>",
                    from_email="elearn@dccaep.org",
                    recipient_list=[obj.student.user.email],
                )
                obj.elearn_status = 'Pending'
                obj.status_updated = datetime.today()
                obj.save()

    def create_g_suite_account(self, request, queryset):

        scopes = ['https://www.googleapis.com/auth/admin.directory.user']

        credentials = ServiceAccountCredentials._from_parsed_json_keyfile(
            keyfile_dict=settings.KEYFILE_DICT,
            scopes=scopes
        )

        shane = credentials.create_delegated('shane.dicks@elearnclass.org')
        http_auth = shane.authorize(Http())
        service = discovery.build('admin', 'directory_v1', http=http_auth)

        for obj in queryset:
            if obj.g_suite_email:
                pass
            else:
                first = obj.student.user.first_name
                last = obj.student.user.last_name
                name = ".".join([first, last])
                x = 0
                def check_email(name, x): # check g_suite for email, add numbers incrementally if email in use until email is valid
                    if x == 0:
                        email = "@".join([name, 'elearnclass.org'])
                        try:
                            user = service.users().get(userKey=email).execute()
                            return check_email(name, x + 1)
                        except:
                            return email
                    else:
                        new_name = "{0}{1}".format(name, x)
                        new_email = "@".join([new_name, 'elearnclass.org'])
                        try:
                            user = service.users().get(userKey=new_email).execute()
                            return check_email(name, x + 1)
                        except:
                            return new_email
                email = check_email(name, x)

                record = {
                    "primaryEmail": email,
                    "name": {
                        "givenName": first,
                        "familyName": last
                    },
                    "password": last + first + "Pass",
                    "externalIds": [
                        {
                            "value": obj.student.WRU_ID,
                            "type": "custom",
                            "customType": "wru"
                        }
                    ],
                }
                service.users().insert(body=record).execute()
                obj.g_suite_email = email
                obj.save()


admin.site.register(ElearnRecord, ElearnRecordAdmin)


class CoachingAdmin(ImportExportActionModelAdmin):

    resource_class = CoachingResource

    list_display = (
        '__str__',
        'coaching_type',
        'active',
        'start_date',
        'end_date',
    )

    search_fields = [
        'coachee__student__user__last_name',
        'coachee__student__user__first_name',
        'coachee__student__WRU_ID',
        'coach__staff__user__last_name',
        'coach__staff__user__last_name'
    ]

    fields = [
        'coach',
        'coaching_type',
        'active',
        'start_date',
        'end_date',
    ]


admin.site.register(Coaching, CoachingAdmin)


class ProfileAdmin(ImportExportActionModelAdmin):

    resource_class = ProfileResource

    list_display = (
        '__str__',
    )

    search_fields = [
        'student__user__last_name',
        'student__user__first_name',
        'student__WRU_ID'
    ]

    fields = [
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


admin.site.register(Profile, ProfileAdmin)


class MeetingNoteAdmin(ImportExportActionModelAdmin):

    resource_class = MeetingNoteResource

    list_display = (
        'coaching',
        'meeting_date',
        'start_time'
    )

    search_fields = [
        'coaching__coachee__student__user__last_name',
        'coaching__coachee__student__user__first_name',
        'coaching__coachee__student__WRU_ID',
        'coaching__coach__staff__user__last_name',
        'coaching__coach__staff__user__first_name',
    ]

    fields = [
        'meeting_type',
        'student_no_show',
        'meeting_date',
        'start_time',
        'end_time',
        'progress',
        'next_steps',
        'notes'
    ]


admin.site.register(MeetingNote, MeetingNoteAdmin)
