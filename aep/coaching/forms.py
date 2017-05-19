from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Row, Column, HTML
from .models import Profile, Coaching, MeetingNote, AceRecord


class ProfileForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
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
