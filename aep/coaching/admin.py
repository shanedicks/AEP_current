from django.contrib import admin

from import_export import resources, fields, widgets
from import_export.admin import ImportExportActionModelAdmin
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
            'elearn_status',
            'status_updated',
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
            'coach',
            'coachee',
            'coaching_type',
            'active',
            'start_date',
            'end_date',
        )


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
        'coachee',
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
