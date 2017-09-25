from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Row, Column, HTML
from .models import Profile, Coaching, MeetingNote, AceRecord, ElearnRecord
from people.models import Staff


class GeneralInfoForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(GeneralInfoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column(
                    'texts_ok',
                    css_class="col-md-4"
                ),
                Column(
                    'smartphone',
                    css_class="col-md-4"
                ),
                Column(
                    'webcam',
                    css_class="col-md-4"
                ),
            ),
            Field(
                'device',
            ),
            Field(
                'contact_preference',
                'other_contact',
                'availability',
                'other_availability',
                wrapper_class='col-md-6'
            ),
            'library',
            Field(
                'instagram',
                'twitter',
                'facebook',
                'linkedin',
                wrapper_class='col-md-6'
            ),
            HTML(
                '<hr><h4>Are you interested in any of the following ACE Pathways?</h4>'
            ),
            Row(
                Column(
                    'health_pathway_interest',
                    css_class="col-md-3"
                ),
                Column(
                    'crafts_pathway_interest',
                    css_class="col-md-3"
                ),
                Column(
                    'it_pathway_interest',
                    css_class="col-md-3"
                ),
                Column(
                    'hospitality_pathway_interest',
                    css_class="col-md-3"
                )
            )
        )

    class Meta:
        model = Profile
        fields = (
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
        )


class AcademicQuestionaireForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(AcademicQuestionaireForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            HTML(
                '<h4>This section is about your time in School</h4>'
            ),
            'grade_level',
            'school_experience',
            'special_help',
            'special_help_desc',
            'conditions',
            'elearn_experience',
            HTML(
                '<h4>How do you feel about the following subjects?</h4>'
            ),
            Field(
                'math',
                'english',
                'social_studies',
                wrapper_class='col-md-4'
            ),
            Field(
                'best_classes',
                'worst_classes',
            ),
            'favorite_subject',
        )

    class Meta:
        model = Profile
        fields = (
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
        )


class PersonalQuestionaireForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(PersonalQuestionaireForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'completion_time',
            'hours_per_week',
            'personal_goal',
            'frustrated',
            'anything_else'
        )

    class Meta:
        model = Profile
        fields = (
            'completion_time',
            'hours_per_week',
            'personal_goal',
            'frustrated',
            'anything_else'
        )

        labels = {
            'anything_else': 'Tell us a little about yourself - '
                             'whatever you feel comfortable sharing'
        }


class ProfileForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            Row(
                Column(
                    'texts_ok',
                    css_class="col-md-4"
                ),
                Column(
                    'smartphone',
                    css_class="col-md-4"
                ),
                Column(
                    'webcam',
                    css_class="col-md-4"
                ),
            ),
            Field(
                'device',
            ),
            Field(
                'contact_preference',
                'other_contact',
                'availability',
                'other_availability',
                wrapper_class='col-md-6'
            ),
            'library',
            Field(
                'instagram',
                'twitter',
                'facebook',
                'linkedin',
                wrapper_class='col-md-6'
            ),
            HTML(
                '<hr><h4>Are you interested in any of the following ACE Pathways?</h4>'
            ),
            Row(
                Column(
                    'health_pathway_interest',
                    css_class="col-md-3"
                ),
                Column(
                    'crafts_pathway_interest',
                    css_class="col-md-3"
                ),
                Column(
                    'it_pathway_interest',
                    css_class="col-md-3"
                ),
                Column(
                    'hospitality_pathway_interest',
                    css_class="col-md-3"
                ),
            ),
            HTML(
                '<h4>This section is about your time in School</h4>'
            ),
            'grade_level',
            'school_experience',
            'special_help',
            'special_help_desc',
            'conditions',
            'elearn_experience',
            HTML(
                '<h4>How do you feel about the following subjects?</h4>'
            ),
            Field(
                'math',
                'english',
                'social_studies',
                wrapper_class='col-md-4'
            ),
            Field(
            'best_classes',
            'worst_classes',
            ),
            'favorite_subject',
            'completion_time',
            'hours_per_week',
            'personal_goal',
            'frustrated',
            'anything_else'
        )

    class Meta:
        model = Profile
        fields = (
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

        labels = {
            'anything_else': 'Tell us a little about yourself - '
                             'whatever you feel comfortable sharing'
        }


class MeetingNoteForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(MeetingNoteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            Fieldset(
                'Meeting Info',
                'meeting_type',
                Field(
                    'meeting_date',
                    placeholder="MM/DD/YYYY",
                    wrapper_class="col-md-4",
                    data_mask="99/99/9999"
                ),
                Field(
                    'start_time',
                    placeholder="HH:MM AM/PM",
                    wrapper_class="col-md-4",
                    data_mask="99:99 aa"
                ),
                Field(
                    'end_time',
                    placeholder="HH:MM AM/PM",
                    wrapper_class="col-md-4",
                    data_mask="99:99 aa"
                ),
            ),
            Fieldset(
                'Meeting Outcomes',
                Column(
                    'student_no_show',
                    'student_reschedule',
                    css_class='col-md-6'
                ),
                Column(
                    'student_cancel',
                    'coach_cancel',
                    css_class='col-md-6'
                ),
            ),
            Fieldset(
                'Student Status',
                Column(
                    'low_grades',
                    'class_absences',
                    css_class='col-md-4'
                ),
                Column(
                    'cannot_reach',
                    'meeting_absences',
                    css_class='col-md-4'
                ),
                Column(
                    'ace_withdrawl',
                    css_class='col-md-4'
                ),
            ),
            'progress',
            'next_steps',
            'notes'
        )

    class Meta:
        model = MeetingNote
        fields = (
            'meeting_type',
            'meeting_date',
            'start_time',
            'end_time',
            'student_no_show',
            'student_reschedule',
            'student_cancel',
            'coach_cancel',
            'low_grades',
            'class_absences',
            'meeting_absences',
            'cannot_reach',
            'ace_withdrawl',
            'progress',
            'next_steps',
            'notes'
        )


class AssignCoach(ModelForm):

    def __init__(self, *args, **kwargs):
        qst = Staff.objects.filter(coach=True)
        self.base_fields['coach'].queryset = qst
        super(AssignCoach, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field(
                'coach',
                'coaching_type',
            ),
            Field(
                'start_date',
                placeholder="MM/DD/YYYY",
                data_mask="99/99/9999"
            ),
        )

    class Meta:
        model = Coaching
        fields = (
            'coach',
            'start_date',
            'coaching_type',
        )


class AceRecordForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(AceRecordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    class Meta:
        model = AceRecord
        fields = (
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
        )


class ElearnRecordForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ElearnRecordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

    class Meta:
        model = ElearnRecord
        fields = (
            'elearn_status',
            'status_updated',
            'intake_date'
        )
