from datetime import datetime
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import Form, ModelForm, CharField, ValidationError, DateField, FileField
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Submit, Row, Column, HTML, Div
from crispy_forms.bootstrap import PrependedText
from .models import Student, Staff, WIOA, CollegeInterest, Prospect, ProspectNote, Paperwork


def make_username(first_name, last_name):
    if len(last_name) < 5:
        name = "{0}{1}".format(
            first_name[0],
            last_name.replace(
                ' ',
                ''
            ).replace("'", "")
        ).lower()
    else:
        name = "{0}{1}".format(
            first_name[0],
            last_name.replace(
                ' ',
                ''
            ).replace("'", "")[:5]
        ).lower()
    x = 0
    while True:
        if x == 0 and User.objects.filter(username=name).count() == 0:
            return name
        else:
            new_name = "{0}{1}".format(name, x)
            if User.objects.filter(username=new_name).count() == 0:
                return new_name
        x += 1


phone_validator = RegexValidator(
    regex=r'^[2-9]\d{2}-\d{3}-\d{4}$',
    message='Please enter a valid phone number',
    code='invalid_phone'
)

zip_code_validator = RegexValidator(
    regex = r'^\d{5}(?:-\d{4})?$',
    message='Please enter a valid US zip code. Format: ##### or #####-####',
    code='invalid zip code'
)

class StudentComplianceForm(ModelForm):

    class Meta:
        model = Student

        fields = (
            'paperwork',
            'folder',
            'orientation',
            'intake_form',
            'intake_quiz'
        )

        labels = {
            'paperwork': 'Intake Paperwork Completed',
            'orientation': 'Attended Orientation',
            'folder': ' Office Folder Completed',
            'intake_form': 'Intake Form Completed',
            'intake_quiz': 'Orientation Quiz Completed'
        }

    def __init__(self, *args, **kwargs):
        super(StudentComplianceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            Field(
                'folder',
                'orientation',
                'paperwork',
                'intake_form',
                'intake_quiz'
            )
        )


class StudentSearchForm(Form):
    f_name = CharField(label=_('First Name'), required=False)
    l_name = CharField(label=_('Last Name'), required=False)
    stu_id = CharField(label=_('Student ID'), required=False)
    dob = DateField(label=_('Date of Birth'), required=False)

    def filter_queryset(self, request, queryset):
        qst = queryset
        if self.cleaned_data['f_name']:
            qst = qst.filter(
                first_name__icontains=self.cleaned_data['f_name']
            )
        if self.cleaned_data['l_name']:
            qst = qst.filter(
                last_name__icontains=self.cleaned_data['l_name']
            )
        if self.cleaned_data['stu_id']:
            qst = qst.filter(
                WRU_ID__contains=self.cleaned_data['stu_id']
            )
        if self.cleaned_data['dob']:
            qst = qst.filter(dob=self.cleaned_data['dob'])
        return qst


class CollegeInterestForm(ModelForm):

    class Meta:
        model = CollegeInterest
        fields = (
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
        )

    def __init__(self, *args, **kwargs):
        super(CollegeInterestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                'Adult Ed Information',
                'ged_hiset',
                'current_adult_ed',
                'adult_ed_location',
            ),
            Fieldset(
                'Prior College History',
                'other_college',
                'other_college_location',
                'other_college_name',
            ),
            Fieldset(
                'Have you ever taken for-credit classes'
                ' at any of these LCTCS colleges?',
                Row(
                    Column(
                        'bpcc',
                        'brcc',
                        'ctcc',
                        'dcc',
                        'ldcc',
                        css_class='col-md-4'
                    ),
                    Column(
                        'ftcc',
                        'ntcc',
                        'ncc',
                        'nltc',
                        css_class='col-md-4'
                    ),
                    Column(
                        'rpcc',
                        'scl',
                        'slcc',
                        'sowela',
                        css_class='col-md-4'
                    )
                ),
                'lola',
            ),
            Fieldset(
                'Financial Aid Information',
                'prev_balance',
                'financial_aid',
                'aid_status',
                'nslds_notes',
            ),
            Fieldset(
                'Please indicate which FAFSAs you have completed.',
                'fafsa1617',
                'fafsa1718',
                'fafsa1819',
            ),
            Fieldset(
                'Prior Coursework',
                'delgado_classes',
                'workforce_training',
                'workforce_training_desc'
            ),
            Fieldset(
                'Have you ever earned any industry-based certifications?',
                'serv_safe',
                'nccer',
                'ic3',
                'first_aid',
                'cpr',
            ),
            Fieldset(
                'Employment Details',
                'employment_status',
                'work_schedule',
            ),
            Field(
                'career_goals',
                'notes'
            ),
        )


class UserForm(ModelForm):

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email'
        )
        labels = {
            'first_name': "First Name (primer y segundo nombre)",
            'last_name': "Last Name (primer y segundo apellido)"
        }

        help_texts = {
            'email': "If you're hoping to take online classes we will need a valid email."
        }

    def save(self):
        user = super(UserForm, self).save(commit=False)
        user.username = make_username(first_name, last_name)
        user.password = User.objects.make_random_password()
        user.save()
        return user

    def clean_first_name(self):
        data = self.cleaned_data['first_name'].title()
        return data

    def clean_last_name(self):
        data = self.cleaned_data['last_name'].title()
        return data

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            Fieldset(
                'User Information',
                Row(
                    Field(
                        'first_name',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                    Field(
                        'last_name',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                ),
                'email'
            )
        )


class UserUpdateForm(ModelForm):

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email'
        )
        labels = {
            'first_name': "First Name (primer y segundo nombre)",
            'last_name': "Last Name (primer y segundo apellido)"
        }

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            Fieldset(
                'User Information',
                Row(
                    Field(
                        'first_name',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                    Field(
                        'last_name',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                ),
                'email'
            )
        )


class StudentPersonalInfoForm(ModelForm):

    def clean_dob(self):
        data = self.cleaned_data['dob']
        diff = timezone.now().date() - data
        age = diff.days // 365.25
        if age < 16:
            raise ValidationError(
                "We're Sorry, but you must be at least 16 years of age"
                " in order to enroll in classes."
            )
        elif age < 18:
            raise ValidationError(
                "If you are 16 or 17 years old additional paperwork is "
                "required for you to register for classes.  Please come "
                "to the Adult Education Office, City Park Campus, 615 "
                "City Park Avenue, Building 7, Room 170.  Our office hours"
                " are Monday thru Thursday, 9am to 4pm.  If you have any "
                "questions, please contact us at 504-671-5434."
            )
        return data

    def clean_first_name(self):
        data = self.cleaned_data['first_name'].title()
        return data

    def clean_last_name(self):
        data = self.cleaned_data['last_name'].title()
        return data

    def __init__(self, *args, **kwargs):
        super(StudentPersonalInfoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Fieldset(
                'Personal Information',
                Row(
                    Field(
                        'first_name',
                        wrapper_class="col-md-6",
                        required=True,
                    ),
                    Field(
                        'last_name',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                ),
                HTML(
                    """<strong><p>Optional (opcional)</p></strong>
                    <p>Please let us know how to better address you (Háganos saber cómo dirigirnos mejor a usted)</p>"""
                ),
                Row(
                    Field(
                    'title',
                    wrapper_class="col-md-3",
                    required=True,
                    ),
                    Field(
                    'nickname',
                    wrapper_class="col-md-6"
                    ),
                    Field(
                    'pronoun',
                    wrapper_class="col-md-3",
                    ),
                ),
                'email',
                Row(
                    Field(
                        'dob',
                        placeholder="MM/DD/YYYY",
                        wrapper_class="col-md-4",
                        data_mask="99/99/9999",
                        required=True
                    ),
                    Field(
                        'gender',
                        'marital_status',
                        wrapper_class="col-md-4",
                        required=True
                    ),
                ),
                Row(
                    Field(
                        'other_ID',
                        'other_ID_name',
                        wrapper_class="col-md-6"
                    )
                ),
                'US_citizen',
            ),
        )

    class Meta:
        model = Student
        fields = (
            "first_name",
            "last_name",
            "pronoun",
            "nickname",
            "title",
            "email",
            "dob",
            "gender",
            "marital_status",
            "US_citizen",
            "other_ID",
            "other_ID_name",
        )
        labels = {
            'first_name': "First Name (primer y segundo nombre)*",
            'last_name': "Last Name (primer y segundo apellido)*",
            'title': "Title (titulo)*",
            'nickname': "Preferred Name or Nickname (nombre o apodo preferido)",
            'pronoun': "Pronouns (pronombres)",
            "US_citizen": "<strong>Check this box if you are a US Citizen*</strong>"
        }


class StudentInterestForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(StudentInterestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Fieldset(
                'Tell us about your goals',
                'primary_goal',
                HTML(
                    """<p><strong>What other goals would you like to pursue? (optional)</strong></p>"""
                ),
                Column(
                    "check_goal_1",
                    "check_goal_2",
                    "check_goal_3",
                    css_class="col-md-4"
                ),
                Column(
                    "check_goal_4",
                    "check_goal_5",
                    "check_goal_6",
                    css_class="col-md-4"
                ),
                Column(
                    "check_goal_7",
                    "check_goal_8",
                    "check_goal_9",
                    css_class="col-md-4"
                )
            ),
            Fieldset(
                'What types of classes are you interested in taking with us?',
                Column(
                    'ccr_app',
                    'e_learn_app',
                    css_class="col-md-4"
                ),
                Column(
                    'accuplacer_app',
                    'success_app',
                    'certifications_app',
                    css_class="col-md-4"
                ),
                Column(
                    'ell_app',
                    'ell_online_app',
                    css_class="col-md-4"
                ),
            ),
            Fieldset(
                'Tell us more about your class preferences',
                Column(    
                    HTML(
                        """<p><strong>How would you prefer to attend classes? (Check all that apply)</strong></p>"""
                    ),
                    "on_campus",
                    "online_solo",
                    "online_cohort",
                    "hybrid",
                    css_class="col-md-4"
                ),
                Column(
                    HTML(
                        """<p><strong>When would you prefer to attend classes? (Check all that apply)</strong></p>"""
                    ),
                    "morning",
                    "afternoon",
                    "evening",
                    "weekend",
                    css_class="col-md-4"
                ),
                Column(
                    HTML(
                        """<p><strong>Can you access online classes or resources?</strong></p>"""
                    ),
                    "computer_access",
                    "internet_access",
                    css_class="col-md-4"
                )
            ),
            'prior_registration',  
        )

    class Meta:
        model = Student
        fields = (
            "ccr_app",
            "ell_app",
            "success_app",
            'e_learn_app',
            'accuplacer_app',
            'ell_online_app',
            'certifications_app',
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
            "online_cohort",
            "online_solo",
            "on_campus",
            "hybrid",
            "morning",
            "afternoon",
            "evening",
            "weekend",
            "computer_access",
            "internet_access",
            "prior_registration"
        )

        labels = {
            "ccr_app": "In Person study for HiSET",
            "ell_app": "In Person English Language Learners",
            "ell_online_app": "Online English Language Learners",
            "success_app": "Success Classes",
            'e_learn_app': "Online study for HiSET",
            'accuplacer_app': "Accuplacer",
            'certifications_app': 'Certification'
        }

        help_texts = {
            "ccr_app": "(high school equivalency test, was the GED)<br />Math, Science, Social Studies, Reading and Writing",
            "ell_app": "(not a native English speaker)<br />Aprendices del idioma inglés en persona<br />(no un hablante nativo de inglés)",
            "ell_online_app": "(not a native English speaker)<br />Aprendices del idioma inglés en persona<br />(no un hablante nativo de inglés)",
            "success_app": "(examples: Citizenship, Computer Basics, Public Speaking)",
            'e_learn_app': "(high school equivalency test, was the GED)<br />Math, Science, Social Studies, Reading and Writing ",
            'accuplacer_app': "study for college entrance exams",
            'certifications_app': '(NCCER, ServSafe, Basic Life Support, Microsoft Word)'
        }


class StudentContactForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(StudentContactForm, self).__init__(*args, **kwargs)
        self.fields['phone'].validators.append(phone_validator)
        self.fields['alt_phone'].validators.append(phone_validator)
        self.fields['zip_code'].validators.append(zip_code_validator)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Fieldset(
                'Contact Information',
                Row(
                    Field(
                        'phone',
                        placeholder="504-555-5555",
                        wrapper_class="col-md-6",
                        data_mask="999-999-9999",
                        required=True
                    ),
                    Field(
                        'alt_phone',
                        wrapper_class="col-md-6",
                        placeholder="504-555-5555",
                        data_mask="999-999-9999",
                    )
                ),
                Row(
                    Field(
                        'street_address_1',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                    Field(
                        'street_address_2',
                        wrapper_class="col-md-6"
                    )
                ),
                Row(
                    Field(
                        'city',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                     Field(
                        'other_city',
                        wrapper_class="col-md-6",
                    ),                   
                    Field(
                        'state',
                        'parish',
                        wrapper_class="col-md-4",
                        required=True
                    ),
                    Field(
                        'zip_code',
                        data_mask="99999",
                        wrapper_class="col-md-4",
                        required=True
                    ),
                ),
            ),
            Fieldset(
                'Emergency Contact Information',
                Field(
                    'emergency_contact',
                    required=True,
                ),
                Field(
                    'ec_phone',
                    data_mask="999-999-9999",
                    wrapper_class="col-md-4",
                    required=True
                ),
                Field(
                    'ec_email',
                    wrapper_class="col-md-4",
                ),
                Field(
                    'ec_relation',
                    wrapper_class="col-md-4",
                    required=True
                ),
            ),
        )

    class Meta:
        model = Student
        fields = (
            "phone",
            "alt_phone",
            "street_address_1",
            "street_address_2",
            "city",
            "other_city",
            "state",
            "parish",
            "zip_code",
            "emergency_contact",
            "ec_phone",
            "ec_email",
            "ec_relation",
        )

        labels = {
            "emergency_contact": "Emergency Contact Full Name*",
            "ec_phone": "Their Phone Number*",
            "ec_relation": "Their Relationship to You*",
        }


class StudentUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(StudentUpdateForm, self).__init__(*args, **kwargs)
        self.fields['phone'].validators.append(phone_validator)
        self.fields['alt_phone'].validators.append(phone_validator)
        self.fields['zip_code'].validators.append(zip_code_validator)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Fieldset(
                'Student Information',
                Row(
                    Field(
                        'first_name',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                    Field(
                        'last_name',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                ),
                Row(
                    Field(
                        'dob',
                        placeholder="MM/DD/YYYY",
                        wrapper_class="col-md-4",
                        data_mask="99/99/9999"
                    ),
                    Field(
                        'gender',
                        'marital_status',
                        wrapper_class="col-md-4",
                    ),
                ),
                Row(
                    Field(
                    'title',
                        wrapper_class="col-md-3",
                    ),
                    Field(
                        'nickname',
                        wrapper_class="col-md-6"
                    ),
                    Field(
                        'pronoun',
                        wrapper_class="col-md-3"
                    ),
                ),
            ),   
            Fieldset(
                'Contact Information',
                "allow_texts",
                Row(
                    Field(
                        'phone',
                        placeholder="504-555-5555",
                        wrapper_class="col-md-5",
                        data_mask="999-999-9999",
                    ),
                    Field(
                        'alt_phone',
                        wrapper_class="col-md-5",
                        placeholder="504-555-5555",
                        data_mask="999-999-9999",
                    )
                ),
                Row(
                    Field(
                        'email',
                        wrapper_class="col-md-6"
                    ),
                    Field(
                        'alt_email',
                        wrapper_class="col-md-6"
                    ),
                ),
                Row(
                    Field(
                        'street_address_1',
                        wrapper_class="col-md-6",
                    ),
                    Field(
                        'street_address_2',
                        wrapper_class="col-md-6"
                    )
                ),
                Row(
                    Field(
                        'city',
                        wrapper_class="col-md-6",
                    ),
                     Field(
                        'other_city',
                        wrapper_class="col-md-6",
                    ),                   
                    Field(
                        'state',
                        'parish',
                        wrapper_class="col-md-4",
                    ),
                    Field(
                        'zip_code',
                        data_mask="99999",
                        wrapper_class="col-md-4",
                    ),
                ),
            ),
            Fieldset(
                'Emergency Contact Information',
                Field(
                    'emergency_contact',
                ),
                Field(
                    'ec_phone',
                    data_mask="999-999-9999",
                    wrapper_class="col-md-4",
                ),
                Field(
                    'ec_email',
                    wrapper_class="col-md-4",
                ),
                Field(
                    'ec_relation',
                    wrapper_class="col-md-4",
                ),
            ),
            Fieldset(
                'What types of classes are you interested in taking with us?',
                Column(
                    'ccr_app',
                    'ell_app',
                    'accuplacer_app',
                    'success_app',
                    css_class="col-md-6"
                ),
                Column(
                    'e_learn_app',
                    'ell_online_app',
                    'certifications_app',
                    css_class="col-md-6"
                ),
            ),
            Fieldset(
                'Tell us more about your class preferences',
                HTML(
                    """<p><strong>How would you prefer to attend classes? (Check all that apply)</strong></p>"""
                ),
                "on_campus",
                "online_solo",
                "online_cohort",
                "hybrid",
                HTML(
                    """<p><strong>When would you prefer to attend classes? (Check all that apply)</strong></p>"""
                ),
                "morning",
                "afternoon",
                "evening",
                "weekend",
                HTML(
                    """<p><strong>Can you access online classes or resources?</strong></p>"""
                ),
                "computer_access",
                "internet_access"
            ),
        )

    class Meta:
        model = Student
        fields = (
            "first_name",
            "last_name",
            'title',
            'nickname',
            'pronoun',
            "email",
            "alt_email",
            "dob",
            "gender",
            "marital_status",
            "phone",
            "allow_texts",
            "alt_phone",
            "street_address_1",
            "street_address_2",
            "city",
            "other_city",
            "state",
            "parish",
            "zip_code",
            "emergency_contact",
            "ec_phone",
            "ec_email",
            "ec_relation",
            "on_campus",
            "online_solo",
            "online_cohort",
            "hybrid",
            "morning",
            "afternoon",
            "evening",
            "weekend",
            "internet_access",
            "computer_access",
            'ccr_app',
            'ell_app',
            'accuplacer_app',
            'success_app',
            'e_learn_app',
            'ell_online_app',
            'certifications_app',
        )
        labels = {
            "allow_texts": "Allow Texts",
            "other_city": "Other City Not Listed"
        }


class StudentForm(ModelForm):

    def clean_dob(self):
        data = self.cleaned_data['dob']
        diff = timezone.now().date() - data
        age = diff.days // 365.25
        if age < 16:
            raise ValidationError(
                "We're Sorry, but you must be at least 16 years of age"
                " in order to enroll in classes."
            )
        return data

    def clean_first_name(self):
        data = self.cleaned_data['first_name'].title()
        return data

    def clean_last_name(self):
        data = self.cleaned_data['last_name'].title()
        return data

    def clean_street_address_1(self):
        data = self.cleaned_data['street_address_1'].title()
        return data

    def clean_street_address_2(self):
        data = self.cleaned_data['street_address_2'].title()
        return data

    def clean_emergency_contact(self):
        data = self.cleaned_data['emergency_contact'].title()
        return data

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.fields['phone'].validators.append(phone_validator)
        self.fields['alt_phone'].validators.append(phone_validator)
        self.fields['zip_code'].validators.append(zip_code_validator)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Fieldset(
                'Student Information',
                Row(
                    Field(
                        'first_name',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                    Field(
                        'last_name',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                ),
                Row(
                    Field(
                    'title',
                        wrapper_class="col-md-3",
                        required=True,
                    ),
                    Field(
                        'nickname',
                        wrapper_class="col-md-6"
                    ),
                    Field(
                        'pronoun',
                        wrapper_class="col-md-3"
                    ),
                ),
                Row(
                    Field(
                        'email',
                        wrapper_class="col-md-6"
                    ),
                    Field(
                        'alt_email',
                        wrapper_class="col-md-6"
                    ),
                )
            ),
            Fieldset(
                'Tell us about your goals',
                'primary_goal',
                HTML(
                    """<p><strong>What other goals would you like to pursue? (optional)</strong></p>"""
                ),
                Column(
                    "check_goal_1",
                    "check_goal_2",
                    "check_goal_3",
                    css_class="col-md-4"
                ),
                Column(
                    "check_goal_4",
                    "check_goal_5",
                    "check_goal_6",
                    css_class="col-md-4"
                ),
                Column(
                    "check_goal_7",
                    "check_goal_8",
                    "check_goal_9",
                    css_class="col-md-4"
                )
            ),
            Fieldset(
                'What types of classes are you interested in taking with us?',
                Column(
                    'ccr_app',
                    'ell_app',
                    'accuplacer_app',
                    'success_app',
                    css_class="col-md-6"
                ),
                Column(
                    'e_learn_app',
                    'ell_online_app',
                    'certifications_app',
                    css_class="col-md-6"
                ),
            ),
            Fieldset(
                'Tell us more about your class preferences',
                HTML(
                    """<p><strong>How would you prefer to attend classes? (Check all that apply)</strong></p>"""
                ),
                "on_campus",
                "online_solo",
                "online_cohort",
                "hybrid",
                HTML(
                    """<p><strong>When would you prefer to attend classes? (Check all that apply)</strong></p>"""
                ),
                "morning",
                "afternoon",
                "evening",
                "weekend",
                HTML(
                    """<p><strong>Can you access online classes or resources?</strong></p>"""
                ),
                "computer_access",
                "internet_access"
            ),
            'prior_registration',            
            Fieldset(
                'Contact Information',
                "allow_texts",
                Row(
                    Field(
                        'phone',
                        placeholder="504-555-5555",
                        wrapper_class="col-md-5",
                        data_mask="999-999-9999",
                        required=True
                    ),
                    Field(
                        'alt_phone',
                        wrapper_class="col-md-5",
                        placeholder="504-555-5555",
                        data_mask="999-999-9999",
                    )
                ),
                Row(
                    Field(
                        'street_address_1',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                    Field(
                        'street_address_2',
                        wrapper_class="col-md-6"
                    )
                ),
                Row(
                    Field(
                        'city',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                     Field(
                        'other_city',
                        wrapper_class="col-md-6",
                    ),                   
                    Field(
                        'state',
                        'parish',
                        wrapper_class="col-md-4",
                        required=True
                    ),
                    Field(
                        'zip_code',
                        data_mask="99999",
                        wrapper_class="col-md-4",
                        required=True
                    ),
                ),
            ),
            Fieldset(
                'Emergency Contact Information',
                Field(
                    'emergency_contact',
                    required=True,
                ),
                Field(
                    'ec_phone',
                    data_mask="999-999-9999",
                    wrapper_class="col-md-4",
                    required=True
                ),
                Field(
                    'ec_email',
                    wrapper_class="col-md-4",
                ),
                Field(
                    'ec_relation',
                    wrapper_class="col-md-4",
                    required=True
                ),
            ),
            Fieldset(
                'Personal Information',
                'US_citizen',
                Row(
                    Field(
                        'dob',
                        placeholder="MM/DD/YYYY",
                        wrapper_class="col-md-4",
                        data_mask="99/99/9999"
                    ),
                    Field(
                        'gender',
                        'marital_status',
                        wrapper_class="col-md-4",
                    ),
                ),
                Row(
                    Field(
                        'other_ID',
                        'other_ID_name',
                        wrapper_class="col-md-6"
                    )
                )
            ),
        )

    class Meta:
        model = Student
        fields = (
            "first_name",
            "last_name",
            'title',
            'nickname',
            'pronoun',
            "email",
            "alt_email",
            "dob",
            "gender",
            "marital_status",
            "US_citizen",
            "other_ID",
            "other_ID_name",
            "ccr_app",
            "ell_app",
            'ell_online_app',
            "success_app",
            'e_learn_app',
            'accuplacer_app',
            'certifications_app',
            "prior_registration",
            "phone",
            "allow_texts",
            "alt_phone",
            "street_address_1",
            "street_address_2",
            "city",
            "other_city",
            "state",
            "parish",
            "zip_code",
            "emergency_contact",
            "ec_phone",
            "ec_email",
            "ec_relation",
            "primary_goal",
            "check_goal_1",
            "check_goal_2",
            "check_goal_3",
            "check_goal_4",
            "check_goal_5",
            "check_goal_6",
            "check_goal_7",
            "check_goal_8",
            "check_goal_9",
            "on_campus",
            "online_solo",
            "online_cohort",
            "hybrid",
            "morning",
            "afternoon",
            "evening",
            "weekend",
            "internet_access",
            "computer_access"
        )
        labels = {
            "allow_texts": "Allow Texts",
            "US_citizen": "<strong>Check this box if you are a US citizen</strong>",
            "ccr_app": "In Person study for HiSET",
            "ell_app": "In Person English Language Learners",
            "ell_online_app": "Online English Language Learners",
            "success_app": "Success Classes",
            'e_learn_app': "Online study for HiSET",
            'accuplacer_app': "Accuplacer",
            'certifications_app': 'Certification'
        }

        help_texts = {
            "ccr_app": "(high school equivalency test, was the GED)<br />Math, Science, Social Studies, Reading and Writing",
            "ell_app": "(not a native English speaker)<br />Aprendices del idioma inglés en persona<br />(no un hablante nativo de inglés)",
            "ell_online_app": "(not a native English speaker)<br />Aprendices del idioma inglés en persona<br />(no un hablante nativo de inglés)",
            "success_app": "(examples: Citizenship, Computer Basics, Public Speaking)",
            'e_learn_app': "(high school equivalency test, was the GED)<br />Math, Science, Social Studies, Reading and Writing ",
            'accuplacer_app': "study for college entrance exams",
            'certifications_app': '(NCCER, ServSafe, Basic Life Support, Microsoft Word)'
        }


class PartnerForm(ModelForm):

    def clean_dob(self):
        data = self.cleaned_data['dob']
        diff = timezone.now().date() - data
        age = diff.days // 365.25
        if age < 16:
            raise ValidationError(
                "We're Sorry, but you must be at least 16 years of age"
                " in order to enroll in classes."
            )
        elif age < 18:
            raise ValidationError(
                "If you are 16 or 17 years old additional paperwork is "
                "required for you to register for classes.  Please come "
                "to the Adult Education Office, City Park Campus, 615 "
                "City Park Avenue, Building 7, Room 170.  Our office hours"
                " are Monday thru Thursday, 9am to 4pm.  If you have any "
                "questions, please contact us at 504-671-5434."
            )
        return data

    def clean_first_name(self):
        data = self.cleaned_data['first_name'].title()
        return data

    def clean_last_name(self):
        data = self.cleaned_data['last_name'].title()
        return data

    def clean_street_address_1(self):
        data = self.cleaned_data['street_address_1'].title()
        return data

    def clean_street_address_2(self):
        data = self.cleaned_data['street_address_2'].title()
        return data

    def clean_emergency_contact(self):
        data = self.cleaned_data['emergency_contact'].title()
        return data

    def __init__(self, *args, **kwargs):
        super(PartnerForm, self).__init__(*args, **kwargs)
        self.fields['phone'].validators.append(phone_validator)
        self.fields['alt_phone'].validators.append(phone_validator)
        self.fields['zip_code'].validators.append(zip_code_validator)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Fieldset(
                'Student Information',
                Row(
                    Field(
                        'first_name',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                    Field(
                        'last_name',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                ),
                'email',
                Row(
                    Field(
                        'WRU_ID',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                    Field(
                        'partner',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                ),
                'US_citizen',
                Row(
                    Field(
                        'dob',
                        placeholder="MM/DD/YYYY",
                        wrapper_class="col-md-4",
                        data_mask="99/99/9999"
                    ),
                    Field(
                        'gender',
                        'marital_status',
                        wrapper_class="col-md-4",
                    ),
                ),
            ),
            Fieldset(
                'Student Contact Information',
                Row(
                    Field(
                        'phone',
                        placeholder="504-555-5555",
                        wrapper_class="col-md-6",
                        data_mask="999-999-9999",
                        required=True
                    ),
                    Field(
                        'alt_phone',
                        wrapper_class="col-md-6",
                        placeholder="504-555-5555",
                        data_mask="999-999-9999",
                    )
                ),
                Row(
                    Field(
                        'street_address_1',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                    Field(
                        'street_address_2',
                        wrapper_class="col-md-6"
                    )
                ),
                Row(
                    Field(
                        'city',
                        'state',
                        wrapper_class="col-md-4",
                        required=True
                    ),
                    Field(
                        'zip_code',
                        data_mask="99999",
                        wrapper_class="col-md-4",
                        required=True
                    ),
                ),
                'parish',
            ),
            Fieldset(
                'Student Emergency Contact Information',
                Field(
                    'emergency_contact',
                    required=True
                ),
                Field(
                    'ec_phone',
                    data_mask="999-999-9999",
                    wrapper_class="col-md-4",
                    required=True
                ),
                Field(
                    'ec_email',
                    'ec_relation',
                    wrapper_class="col-md-4"
                ),
            ),
            Fieldset(
                'What types of classes will the student be taking with us?',
                Column(
                    'ccr_app',
                    'ell_app',
                    'ace_app',
                    css_class="col-md-6"
                ),
                Column(
                    'success_app',
                    'e_learn_app',
                    'accuplacer_app',
                    css_class="col-md-6"
                ),
            ),
        )

    class Meta:
        model = Student
        fields = (
            "first_name",
            "last_name",
            "email",
            "WRU_ID",
            "partner",
            "dob",
            "gender",
            "marital_status",
            "ccr_app",
            "ell_app",
            "ace_app",
            "success_app",
            'e_learn_app',
            'accuplacer_app',
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
        )

        labels = {
            "ec_relation": "Their relationship to student",
            "US_citizen": "Check this box if you are a US citizen",
            "ccr_app": "College and Career Readiness (HiSET Prep)",
            "ell_app": "English Language Learning",
            "ace_app": "Accelerated Career Education Program",
            "success_app": "Success Classes",
            'e_learn_app': "Online Classes with eLearn",
            'accuplacer_app': "Accuplacer Prep Classes",
        }

        help_texts = {
            "WRU_ID": "Student's ID number in LCTCS workreadyu database",
            "partner": "Name of Delgado partner organization where this student is registered",
            "ccr_app": "Reading, writing, and math skill building classes to help with college and career readiness goals as well as passing the HiSET.",
            "ell_app": "English classes to help non-native speakers improve speaking, listening, reading, and writing skills.",
            "ace_app": "Integrated education and training classes where students can earn industry credentials and college credit in career pathways: information technology, healthcare, construction trades, and culinary/hospitality.",
            "success_app": "Classes designed to help students successfully navigate school and careers such as computer basics, job readiness, career exploration, college skills, and financial success.",
            'e_learn_app': "Online courses to help with college and career readiness goals as well as passing the HiSET.",
            'accuplacer_app': "Short preparation classes for the English and math accuplacer college placement tests. ",
        }


class SSNForm(ModelForm):

    def clean_SID(self):
        data = self.cleaned_data['SID']
        data = "".join([c for c in data if c.isdigit()])
        if len(data) != 9 or len(set(data)) == 1:
            data = ''
        return data

    def __init__(self, *args, **kwargs):
        super(SSNForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Field(
                "SID",
                data_mask="999-99-9999"
            ),
        )

    class Meta:
        model = WIOA
        fields = (
            'SID',
        )

        help_texts = {
            "SID": "This is used by the State of Louisiana as a means of matching student records, however it is not required for admission."
        }


class REForm(ModelForm):

    def clean(self):
        data = super(REForm, self).clean()
        ethnicity = [
            data['hispanic_latino'],
            data['amer_indian'],
            data['asian'],
            data['black'],
            data['white'],
            data['pacific_islander'],
        ]
        if not any(ethnicity):
            raise ValidationError(
                _('Sorry, the State of Louisiana requires'
                    ' that we collect race/ethnicity data.'
                    'You must check at least one of the boxes.'),
                code=ethnicity
            )

    def __init__(self, *args, **kwargs):
        super(REForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Fieldset(
                'Race/Ethnicity/Language Information*',
                Row(
                    Column(
                        "amer_indian",
                        "asian",
                        css_class="col-md-4"
                    ),
                    Column(
                        "black",
                        "hispanic_latino",
                        css_class="col-md-4",
                    ),
                    Column(
                        "white",
                        "pacific_islander",
                        css_class="col-md-4"
                    ),

                ),
                Row(
                    Field(
                        "country",
                        "native_language",
                        wrapper_class="col-md-6",
                        required=True
                    )
                ),
                Row(
                    Field(
                        "other_country",
                        "other_language",
                        wrapper_class="col-md-6"
                    )
                )
            ),
        )

    class Meta:
        model = WIOA
        fields = (
            "hispanic_latino",
            "amer_indian",
            "asian",
            "black",
            "white",
            "pacific_islander",
            "country",
            "other_country",
            "other_language",
            "native_language",
        )

        labels = {
            "country": "Country of Birth*",
            "native_language": "Native Language*",
        }


class EETForm(ModelForm):

    def clean(self):
        data = super(EETForm, self).clean()
        if data['current_employment_status'] in ["1", "9"]:
            if data["employer"] == '': 
                msg = _("""Sorry, the State of Louisiana requires that we
                        collect employer data from any employed applicants. """)
                self.add_error("employer", msg)
            if data["occupation"] == '':
                msg = _("""Sorry, the State of Louisiana requires that we
                        collect occupation data from any employed applicants. """)
                self.add_error("occupation", msg)

    def __init__(self, *args, **kwargs):
        super(EETForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Fieldset(
                "Educational Details",
                Row(
                    Field(
                        "highest_level_completed",
                        "highet_level_at_entry",
                        "school_location",
                        wrapper_class="col-md-4",
                        required=True
                    ),
                )
            ),
            Fieldset(
                "Employment Details",
                Row(
                    Field(
                        'current_employment_status',
                        wrapper_class="col-md-4",
                        required=True
                    ),
                    Field(
                        "employer",
                        "occupation",
                        wrapper_class="col-md-4"
                    )
                ),
                "long_term_unemployed",
                "current_industry",
                "industry_preference",
                "migrant_seasonal_status",
            ),
        )

    class Meta:
        model = WIOA
        fields = (
            "highest_level_completed",
            "highet_level_at_entry",
            "school_location",
            "current_employment_status",
            "employer",
            "occupation",
            "migrant_seasonal_status",
            "long_term_unemployed",
            "current_industry",
            "industry_preference",
        )


class DisabilityForm(ModelForm):

    def clean_request_accommodation(self):
        data = self.cleaned_data['request_accommodation']
        if not data:
            msg = _("You must indicate you understand your responsibility to request accomodations.")
            self.add_error("request_accommodation", msg)
        return data

    def __init__(self, *args, **kwargs):
        super(DisabilityForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Fieldset(
                "Accessibilitiy Details",
                Row(
                    Column(
                        "adhd",
                        "autism",
                        "deaf_blind",
                        "deaf",
                        "emotional_disturbance",
                        css_class="col-md-4",
                    ),
                    Column(
                        "k12_iep",
                        "hard_of_hearing",
                        "intellectual_disability",
                        "multiple_disabilities",
                        "orthopedic_impairment",
                        css_class="col-md-4",
                    ),
                    Column(
                        "other_health_impairment",
                        "learning_disability",
                        "speech_or_lang_impairment",
                        "traumatic_brain_injury",
                        "visual_impairment",
                        css_class="col-md-4",
                    )
                ),
                HTML(
                    '<h4>Learning Disabilities</h4>'
                ),
                Row(
                    Column(
                        "dyscalculia",
                        "dysgraphia",
                        css_class="col-md-4",
                    ),
                    Column(
                        "dyslexia",
                        "neurological_impairments",
                        css_class="col-md-4",
                    )
                ),
                HTML(
                    "<h4>Disability Disclosure </h4>"
                ),
                Field(
                    'disability_notice',
                    required=True,
                ),
                'request_accommodation'
            ),
        )

    class Meta:
        model = WIOA
        fields = (
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
            "disability_notice",
            "request_accommodation"
        )

        labels = {
            "disability_notice": "Are you an Individual with a Disability?*",
            "request_accommodation": "<strong>Check here to indicate that you understand your responsibility to request accommodations.*</strong>"
        }


class AdditionalDetailsForm(ModelForm):

    def clean_household_size(self):
        data = self.cleaned_data['household_size']
        if data < 1:
            data = 1 
        return data

    def __init__(self, *args, **kwargs):
        super(AdditionalDetailsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Fieldset(
                "Additional Details",
                HTML("""<p>This information is
                     optional, however, sharing it with us can help
                     us to better understand the needs of our
                     student body and provide additional
                     programming and services for all of
                     our students.</p>"""
                ),
                HTML("""<p><strong>Have you 
                    (or someone in your household) recieved any of 
                    the following in the last six months?</strong></p>"""
                ),
                Field(
                    "TANF",
                    "TANF_2",
                    "SNAP",
                    "SSI",
                    "Tstate",
                    wrapper_class="col-md-60"
                ),
                "household_income",
                "household_size",
                HTML("""<p><strong>Do any of the following statements apply to you?</strong></p>"""
                ),
                "displaced_homemaker",
                "single_parent",
                "lacks_adequate_residence",
                "criminal_record",
                "foster_care",
                "veteran",
                Field(
                    "parental_status",
                    required=True,
                ),
                HTML("""<p><strong>I want to increase my involvement in my childrens 
                        education by:</strong></p>"""
                ),
                "help_with_schoolwork",
                "student_teacher_contact",
                "parent_volunteering",
                HTML("""<p><strong>I want to increase my involvement in my childrens 
                    literacy-related activity by:</strong></p>"""
                ),
                "read_to_children",
                "visit_library",
                "purchase_books",                
            ),
            Fieldset(
                "Before you submit",
                Field(
                    "referred_by",
                    "digital_signature",
                    required=True
                ),
            )
        )

    class Meta:
        model = WIOA
        fields = (
            "TANF",
            "TANF_2",
            "SNAP",
            "SSI",
            "Tstate",
            "household_income",
            "household_size",
            "displaced_homemaker",
            "single_parent",
            "lacks_adequate_residence",
            "criminal_record",
            "foster_care",
            "veteran",
            "parental_status",
            "help_with_schoolwork",
            "student_teacher_contact",
            "parent_volunteering",
            "read_to_children",
            "visit_library",
            "purchase_books",
            "referred_by",
            "digital_signature",
        )

        labels = {
            "parental_status": "Are you a parent?*",
            "referred_by": "<strong>How did you hear about us?*</strong>",
            "digital_signature": "DISCLAIMER: By typing your name below, you are signing this application electronically. You agree that your electronic signature is the legal equivalent of your manual signature on this application.*"
        }


class WioaForm(ModelForm):

    def clean(self):
        data = super(WioaForm, self).clean()
        ethnicity = [
            data['hispanic_latino'],
            data['amer_indian'],
            data['asian'],
            data['black'],
            data['white'],
            data['pacific_islander'],
        ]
        if not any(ethnicity):
            msg = _('Sorry, the State of Louisiana requires'
                    ' that we collect race/ethnicity data')
            self.add_error('pacific_islander', msg)
        if data['current_employment_status'] in ["1", "9"]:
            if data["employer"] == '': 
                msg = _("""Sorry, the State of Louisiana requires that we
                        collect employer data from any employed applicants. """)
                self.add_error("employer", msg)
            if data["occupation"] == '':
                msg = _("""Sorry, the State of Louisiana requires that we
                        collect occupation data from any employed applicants. """)
                self.add_error("occupation", msg)

    def clean_household_size(self):
        data = self.cleaned_data['household_size']
        if data < 1:
            data = 1
        return data

    def clean_request_accommodation(self):
        data = self.cleaned_data['request_accommodation']
        if not data:
            raise ValidationError(
                _("You must indicate you understand your responsibility to request accomodations."),
                code="accomodations"
                )
        return data

    def clean_SID(self):
        data = self.cleaned_data['SID']
        data = "".join([c for c in data if c.isdigit()])
        if len(data) != 9 or len(set(data)) == 1:
            data = ''
        return data

    def __init__(self, *args, **kwargs):
        super(WioaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Field(
                "parental_status",
                "veteran",
            ),
            Field(
                "SID",
                data_mask="999-99-9999"
            ),
            Fieldset(
                "Educational Details",
                Row(
                    Field(
                        "highest_level_completed",
                        "highet_level_at_entry",
                        "school_location",
                        wrapper_class="col-md-4",
                        required=True
                    ),
                )
            ),
            Fieldset(
                "Employment Details",
                Row(
                    Field(
                        'current_employment_status',
                        "employer",
                        "occupation",
                        wrapper_class="col-md-4"
                    )
                ),
                "long_term_unemployed",
                "current_industry",
                "industry_preference",
                "migrant_seasonal_status",
            ),
            Fieldset(
                'Race/Ethnicity/Language Information',
                Row(
                    Column(
                        "amer_indian",
                        "asian",
                        css_class="col-md-4"
                    ),
                    Column(
                        "black",
                        "hispanic_latino",
                        css_class="col-md-4",
                    ),
                    Column(
                        "white",
                        "pacific_islander",
                        css_class="col-md-4"
                    ),
                ),
                Row(
                    Field(
                        "country",
                        "native_language",
                        wrapper_class="col-md-6",
                        required=True
                    )
                ),
                Row(
                    Field(
                        "other_country",
                        "other_language",
                        wrapper_class="col-md-6"
                    )
                )
            ),
            Fieldset(
                "Accessibilitiy Details",
                Row(
                    Column(
                        "adhd",
                        "autism",
                        "deaf_blind",
                        "deaf",
                        "emotional_disturbance",
                        css_class="col-md-4",
                    ),
                    Column(
                        "k12_iep",
                        "hard_of_hearing",
                        "intellectual_disability",
                        "multiple_disabilities",
                        "orthopedic_impairment",
                        css_class="col-md-4",
                    ),
                    Column(
                        "other_health_impairment",
                        "learning_disability",
                        "speech_or_lang_impairment",
                        "traumatic_brain_injury",
                        "visual_impairment",
                        css_class="col-md-4",
                    )
                ),
                HTML(
                    '<h4>Learning Disabilities</h4>'
                ),
                Row(
                    Column(
                        "dyscalculia",
                        "dysgraphia",
                        css_class="col-md-4",
                    ),
                    Column(
                        "dyslexia",
                        "neurological_impairments",
                        css_class="col-md-4",
                    )
                ),
                HTML(
                    "<h4>Disability Disclosure </h4>"
                ),
                Field(
                    'disability_notice',
                    required=True
                ),
                'request_accommodation'
            ),
            Fieldset(
                "Additional Details",
                HTML("""<p>This information is
                     optional, however, sharing it with us can help
                     us to better understand the needs of our
                     student body and provide additional
                     programming and services for all of
                     our students.</p>"""
                ),
                HTML("""<p><strong>Have you 
                    (or someone in your household) recieved any of 
                    the following in the last six months?</strong></p>"""
                ),
                Field(
                    "TANF",
                    "TANF_2",
                    "SNAP",
                    "SSI",
                    "Tstate",
                    wrapper_class="col-md-60"
                ),
                "household_income",
                "household_size",
                HTML("""<p><strong>Do any of the following statements apply to you?</strong></p>"""
                ),
                "displaced_homemaker",
                "single_parent",
                "lacks_adequate_residence",
                "criminal_record",
                "foster_care",
                HTML("""<p><strong>I want to increase my involvement in my childrens 
                        education by:</strong></p>"""
                ),
                "help_with_schoolwork",
                "student_teacher_contact",
                "parent_volunteering",
                HTML("""<p><strong>I want to increase my involvement in my childrens 
                    literacy-related activity by:</strong></p>"""
                ),
                "read_to_children",
                "visit_library",
                "purchase_books",                
            ),
            Fieldset(
                "Before you submit",
                Field(
                    "referred_by",
                    "digital_signature",
                    required=True
                ),
            )
        )

    class Meta:
        model = WIOA
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
            "current_industry",
            "industry_preference",
            "TANF",
            "TANF_2",
            "SNAP",
            "SSI",
            "Tstate",
            "veteran",
            "parental_status",
            "migrant_seasonal_status",
            "long_term_unemployed",
            "single_parent",
            "displaced_homemaker",
            "lacks_adequate_residence",
            "criminal_record",
            "foster_care",
            "household_income",
            "household_size",
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
            "highet_level_at_entry",
            "school_location",
            "country",
            "other_country",
            "native_language",
            "other_language",
            "help_with_schoolwork",
            "student_teacher_contact",
            "parent_volunteering",
            "read_to_children",
            "visit_library",
            "purchase_books",
            "referred_by",
            "disability_notice",
            "request_accommodation",
            "digital_signature",
            "SID"
        )

        labels = {
            "veteran": "<strong> Check this box if you are a veteran</strong>",
            "request_accommodation": """<strong>Check here to indicate that you 
                                        understand your responsibility to request 
                                        accommodations.</strong>""",
            "referred_by": "<strong>How did you hear about us?</strong>"
        }
        help_texts = {
            "SID": "This is used by the State of Louisiana as a means of matching student records, however it is not required for admission."
        }


class StaffForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)
        self.fields['phone'].validators.append(phone_validator)
        self.fields['alt_phone'].validators.append(phone_validator)
        self.fields['zip_code'].validators.append(zip_code_validator)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            'dob',
            Fieldset(
                'Contact Info',
                Row(
                    Field(
                        'phone',
                        placeholder="504-555-5555",
                        wrapper_class="col-md-6",
                        data_mask="999-999-9999",
                        required=True
                    ),
                    Field(
                        'alt_phone',
                        wrapper_class="col-md-6",
                        placeholder="504-555-5555",
                        data_mask="999-999-9999",
                    )
                ),
                Row(
                    Field(
                        'street_address_1',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                    Field(
                        'street_address_2',
                        wrapper_class="col-md-6"
                    )
                ),
                Row(
                    Field(
                        'city',
                        'state',
                        wrapper_class="col-md-4",
                        required=True
                    ),
                    Field(
                        'zip_code',
                        data_mask="99999",
                        wrapper_class="col-md-4",
                        required=True
                    ),
                ),
            ),
            Fieldset(
                'Emergency Contact Info',
                'emergency_contact',
                Field(
                    'ec_phone',
                    data_mask="999-999-9999",
                    wrapper_class="col-md-4"
                ),
                Field(
                    'ec_email',
                    'ec_relation',
                    wrapper_class="col-md-4"
                ),
            ),
            'bio',
        )

    class Meta:
        model = Staff
        fields = (
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
            "bio",
        )


class StudentNotesForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(StudentNotesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            'notes'
        )

    class Meta:
        model = Student
        fields = ('notes',)


class ProspectForm(ModelForm):

    def clean_first_name(self):
        data = self.cleaned_data['first_name'].title()
        return data

    def clean_last_name(self):
        data = self.cleaned_data['last_name'].title()
        return data


    def __init__(self, *args, **kwargs):
        super(ProspectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Row(
                Field(
                    'first_name',
                    wrapper_class="col-md-6",
                    required=True
                ),
                Field(
                    'last_name',
                    wrapper_class="col-md-6",
                    required=True
                ),
            ),
            Row(
                Field(
                    'email',
                    wrapper_class="col-md-4",
                ),
                Field(
                    'phone',
                    wrapper_class="col-md-4",
                    data_mask="999-999-9999"
                ),
                Field(
                    'primary_language',
                    wrapper_class="col-md-4",
                    required=True
                )
            ),
            Row(
                Field(
                    'dob',
                    placeholder="MM/DD/YYYY",
                    data_mask="99/99/9999",
                    wrapper_class="col-md-4",
                    required=True
                ),
                Field(
                    'contact_preference',
                    wrapper_class="col-md-4"
                ),
                Field(
                    'contact_time',
                    wrapper_class="col-md-4"
                )
            )
        )

    class Meta:
        model = Prospect
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone',
            'dob',
            'contact_preference',
            'contact_time',
            'primary_language',
        )


class ProspectStatusForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProspectStatusForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            'active',
            'duplicate',
            'for_credit',
            'returning_student'
        )

    class Meta:
        model = Prospect
        fields = (
            'active',
            'duplicate',
            'for_credit',
            'returning_student'
        )


class ProspectLinkStudentForm(ModelForm):
    
    def __init__(self, *args, **kwargs):
        name = kwargs.pop('name', None)
        qst = Student.objects.none()
        if name:
            name = name[0]
            qst = Student.objects.filter(
                Q(first_name__icontains=name) | Q(last_name__icontains=name) | Q(WRU_ID__contains=name),
                duplicate = False
            )
        self.base_fields['student'].queryset = qst
        super(ProspectLinkStudentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            'student'
        )

    class Meta:
        model = Prospect
        fields = ('student',)


class ProspectAssignAdvisorForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.base_fields['advisor'].queryset = Staff.objects.filter(prospect_advisor=True)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            'advisor'
        )

    class Meta:
        model = Prospect
        fields = ('advisor',)    


class ProspectNoteForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProspectNoteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Row(
                Field(
                    'contact_date',
                    wrapper_class="col-md-4",
                ),
                Field(
                    'contact_method',
                    wrapper_class="col-md-4",
                ),
                Field(
                    'successful',
                    wrapper_class="col-md-4"
                ),
            ),
            'notes',
            'returning_student'
        )

    class Meta:
        model = ProspectNote
        fields = (
            'contact_date',
            'contact_method',
            'successful',
            'notes',
            'returning_student'
        )


class PaperworkForm(ModelForm):

    def clean_signature(self):
        data = self.cleaned_data['signature']
        if data == '':
            raise ValidationError(
                _("You must type your name to sign this form electronically."),
                code="signature"
            )
        return data

    def clean_writing_sample(self):
        data = self.cleaned_data['writing_sample']
        if data == '':
            raise ValidationError(
                _("Please write something in the area provided."),
                code="writing_sample"
            )
        return data

    def clean_contract(self):
        data = self.cleaned_data['contract']
        if data == False:
            raise ValidationError(
                _("You must confirm you accept the Student Contract"),
                code='contract'
            )
        return data

    def clean_testing(self):
        data = self.cleaned_data['testing']
        if data == False:
            raise ValidationError(
                _("You must confirm you accept the Testing Agreement"),
                code='testing'
            )
        return data

    def clean_technology(self):
        data = self.cleaned_data['technology']
        if data == False:
            raise ValidationError(
                _("You must confirm you accept the Technology Policy"),
                code='technology'
            )
        return data

    def clean_ferpa(self):
        data = self.cleaned_data['ferpa']
        if data == False:
            raise ValidationError(
                _("You must confirm you accept FERPA and Student Records Policy"),
                code='ferpa'
            )
        return data

    def __init__(self, *args, **kwargs):
        super(PaperworkForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Fieldset(
                'Writing Activity',
                HTML("""<p>Directions</p><p>Please answer the two questions:</p>
                    <ol><li>What are your goals and dreams?</li><li>How will this 
                    program help you?</li></ol><br><i>Keep in mind...</i><ul><li>This 
                    is not a test. Use this space to express yourself. We want to
                    help you with your goals.</li><li>If you have any questions, 
                    ask a staff member</li></ul>
                    """
                ),
                'writing_sample',
            ),
            Fieldset(
                'Self-Disclosure Form',
                HTML("""<p>I recieved special help when I was in school in one 
                    or more of the following areas:</p>"""
                ),
                'sd_reading',
                'sd_math',
                'sd_language',
                'sd_attention',
                'sd_other',
                HTML("""<br><p>What types of special help did you recieve ?</p>"""),
                'sh_self_se',
                "sh_resource_se",
                "sh_title1_read",
                "sh_title1_math",
                "sh_504",
                "sh_medication",
                "sh_other",
                'sh_request'
            ),
            Fieldset(
                'Program Policies',
                'contract',
                'testing',
                'technology',
                'ferpa',
                Row(
                    Field(
                        'signature',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                    Field(
                        'guardian_signature',
                        wrapper_class="col-md-6"
                    ),
                ),
            ),
        )

    class Meta:
        model = Paperwork
        fields = (
            "ferpa",
            "testing",
            "technology",
            "contract",
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
        )

        labels = {
            'signature': 'Signature*',
            'writing_sample': 'Student Writing Sample*',
            "ferpa": """I have read and accept the 
                    <a href="https://www.dccaep.org/FERPA/" target="_blank">
                    FERPA and Student Records Policy*</a>""",
            "testing": """I have read and accept the 
                    <a href="https://www.dccaep.org/testing-agreement/" target="_blank">
                    Testing Agreement*</a>""",
            "technology": """I have read and accept the 
                    <a href="https://www.dccaep.org/tech-policy/" target="_blank"">
                    Technology Policy*</a>""",
            "contract": """I have read and accept the 
                    <a href="https://www.dccaep.org/student-contract" target="_blank">
                    Student Contract*</a>""",
        }
        help_texts = {
            'guardian_signature': '(If student is under 18)'
        }


class PhotoIdForm(ModelForm):

    def clean_photo_id(self):
        file = self.cleaned_data['photo_id']
        if file.content_type not in ['image/png', 'image/jpeg']:
            raise ValidationError(
                _("Sorry that file type is not supported. Please upload a .jpg or .png image")
            )
        return file

    photo_id = FileField()

    def __init__(self, *args, **kwargs):
        super(PhotoIdForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'

    class Meta:
        model = Paperwork

        fields = (
        )