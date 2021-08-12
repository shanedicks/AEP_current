from datetime import datetime
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import Form, ModelForm, CharField, ValidationError, DateField
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Submit, Row, Column, HTML, Div
from crispy_forms.bootstrap import PrependedText
from .models import Student, Staff, WIOA, CollegeInterest, Prospect, ProspectNote


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
        diff = datetime.today().date() - data
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
                        required=True
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
                    wrapper_class="col-md-3"
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
                'email',
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
            'first_name': "First Name (primer y segundo nombre)",
            'last_name': "Last Name (primer y segundo apellido)",
            'title': "Title (titulo)",
            'nickname': "Preferred Name or Nickname (nombre o apodo preferido)",
            'pronoun': "Pronouns (pronombres)"
        }


class StudentInterestForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(StudentInterestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Fieldset(
                'What types of classes are you interested in taking with us?',
                Column(
                    'ccr_app',
                    'esl_app',
                    'ace_app',
                    css_class="col-md-6"
                ),
                Column(
                    'success_app',
                    'e_learn_app',
                    'accuplacer_app',
                    css_class="col-md-6"
                ),
            )
        )

    class Meta:
        model = Student
        fields = (
            "ccr_app",
            "esl_app",
            "ace_app",
            "success_app",
            'e_learn_app',
            'accuplacer_app',
        )

        help_texts = {
            "ccr_app": "Reading, writing, and math skill building classes to help with college and career readiness goals as well as passing the HiSET.",
            "esl_app": "English classes to help non-native speakers improve speaking, listening, reading, and writing skills.",
            "ace_app": "Integrated education and training classes where students can earn industry credentials and college credit in career pathways: information technology, healthcare, construction trades, and culinary/hospitality.",
            "success_app": "Classes designed to help students successfully navigate school and careers such as computer basics, job readiness, career exploration, college skills, and financial success.",
            'e_learn_app': "Online courses to help with college and career readiness goals as well as passing the HiSET.",
            'accuplacer_app': "Short preparation classes for the English and math accuplacer college placement tests. ",
        }


class StudentContactForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(StudentContactForm, self).__init__(*args, **kwargs)
        self.fields['phone'].validators.append(phone_validator)
        self.fields['alt_phone'].validators.append(phone_validator)
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
                'Emergency Contact Information',
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
        )

    class Meta:
        model = Student
        fields = (
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


class StudentForm(ModelForm):

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
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
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
                Row(
                    Field(
                    'title',
                    wrapper_class="col-md-3"
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
                'email',
                'alt_email'
            ),
            Fieldset(
                'What types of classes are you interested in taking with us?',
                Column(
                    'ccr_app',
                    'esl_app',
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
                'Emergency Contact Information',
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
            "esl_app",
            "ace_app",
            "success_app",
            'e_learn_app',
            'accuplacer_app',
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
            "ec_relation",
        )
        labels = {
            "US_citizen": "Check this box if you are a US citizen",
            "ccr_app": "College and Career Readiness (HiSET Prep)",
            "esl_app": "English Language Learning",
            "ace_app": "Accelerated Career Education Program",
            "success_app": "Success Classes",
            'e_learn_app': "Online Classes with eLearn",
            'accuplacer_app': "Accuplacer Prep Classes",
        }

        help_texts = {
            "ccr_app": "Reading, writing, and math skill building classes to help with college and career readiness goals as well as passing the HiSET.",
            "esl_app": "English classes to help non-native speakers improve speaking, listening, reading, and writing skills.",
            "ace_app": "Integrated education and training classes where students can earn industry credentials and college credit in career pathways: information technology, healthcare, construction trades, and culinary/hospitality.",
            "success_app": "Classes designed to help students successfully navigate school and careers such as computer basics, job readiness, career exploration, college skills, and financial success.",
            'e_learn_app': "Online courses to help with college and career readiness goals as well as passing the HiSET.",
            'accuplacer_app': "Short preparation classes for the English and math accuplacer college placement tests. ",
        }


class PartnerForm(ModelForm):

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
            Fieldset(
                'What types of classes will the student be taking with us?',
                Column(
                    'ccr_app',
                    'esl_app',
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
            "esl_app",
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
            "esl_app": "English Language Learning",
            "ace_app": "Accelerated Career Education Program",
            "success_app": "Success Classes",
            'e_learn_app': "Online Classes with eLearn",
            'accuplacer_app': "Accuplacer Prep Classes",
        }

        help_texts = {
            "WRU_ID": "Student's ID number in LCTCS workreadyu database",
            "partner": "Name of Delgado partner organization where this student is registered",
            "ccr_app": "Reading, writing, and math skill building classes to help with college and career readiness goals as well as passing the HiSET.",
            "esl_app": "English classes to help non-native speakers improve speaking, listening, reading, and writing skills.",
            "ace_app": "Integrated education and training classes where students can earn industry credentials and college credit in career pathways: information technology, healthcare, construction trades, and culinary/hospitality.",
            "success_app": "Classes designed to help students successfully navigate school and careers such as computer basics, job readiness, career exploration, college skills, and financial success.",
            'e_learn_app': "Online courses to help with college and career readiness goals as well as passing the HiSET.",
            'accuplacer_app': "Short preparation classes for the English and math accuplacer college placement tests. ",
        }



class SSNForm(ModelForm):

    def clean_SID(self):
        data = self.cleaned_data['SID']
        if data != "":
            if WIOA.objects.filter(SID=data).count() > 0:
                raise ValidationError(
                    "Sorry, we have this SSN in our records "
                    "already. Are you sure you haven't been with us before? "
                    "Please call 504-671-5434 to speak to a staff member."
                )
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
                        wrapper_class="col-md-6"
                    )
                ),
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
            "native_language",
        )


class EETForm(ModelForm):

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
                        "school_location",
                        wrapper_class="col-md-4"
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
                "migrant_seasonal_status",
                "long_term_unemployed",
            ),
            Fieldset(
                "Services/Training Information",
                Field(
                    "adult_one_stop",
                    "youth_one_stop",
                    "voc_rehab",
                    "wagner_peyser",
                    "recieved_training",
                    "etp_name",
                    "etp_program",
                    "etp_CIP_Code",
                    "training_type_1",
                    "training_type_2",
                    "training_type_3",
                    type="hidden"
                ),
                Field(
                    "job_corps",
                    "youth_build",
                    "school_status",
                    required=True
                ),
            ),
        )

    class Meta:
        model = WIOA
        fields = (
            "highest_level_completed",
            "school_location",
            "current_employment_status",
            "employer",
            "occupation",
            "migrant_seasonal_status",
            "long_term_unemployed",
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
            "job_corps",
            "youth_build",
            "school_status",
        )


class DisabilityForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(DisabilityForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Fieldset(
                "Disability Disclosure",
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
                    '<h5>Learning Disabilities</h5>'
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
                )
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
        )


class AdditionalDetailsForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(AdditionalDetailsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Fieldset(
                "Additional Details",
                Row(
                    HTML("""<div class="col-md-8"><p>This information is
                         optional, however, sharing it with us can help
                         us to better understand the needs of our
                         student body and provide additional
                         programming and services for all of
                         our students.</p></div>"""),
                ),
                Row(
                    Column(
                        "single_parent",
                        "rural_area",
                        "displaced_homemaker",
                        "dislocated_worker",
                        "state_payed_foster",
                        css_class="col-md-4"
                    ),
                    Column(
                        "cult_barriers_hind_emp",
                        "in_foster_care",
                        "aged_out_foster_care",
                        "exhaust_tanf",
                        css_class="col-md-4"
                    ),
                ),
                HTML("""<hr>"""),
                "recieves_public_assistance",
                Row(
                    Column(
                        HTML(
                            """<p>(i) SNAP or Louisiana Purchase Card </p>
                            <p>(ii) TANF Assistance</p>
                            <p>(iii) SSI Assistance</p>"""
                        ),
                        css_class="col-md-4"
                    ),
                    Column(
                        HTML(
                            """<p>(iv) State or local income-based public
                             assistance (Louisiana Medicaid, Section 8 Housing,
                             Kinship Care, Child Care Assisstance,
                             LSU Hospital Free Care, Free Dental Program)</p>"""
                        ),
                        css_class="col-md-4"
                    ),
                ),
                HTML("""<hr>"""),
                Field(
                    "low_family_income",
                    HTML("""<table class="table table-condensed">
                        <tr>
                        <th>Individual</th><th>Family of 2</th>
                        <th>Family of 3</th><th>Family of 4</th>
                        <th>Family of 5</th><th>Family of 6</th>
                        <th>Family of 7</th><th>Family of 8</th>
                        </tr>
                        <tr>
                        <td>$11,880</td><td>$16,020</td><td>$20,300</td>
                        <td>$25,062</td><td>$29,579</td><td>$34,595</td>
                        <td>$36,730</td><td>$40,890</td>
                        </tr></table>"""
                         ),
                    Field(
                        "disabled_in_poverty",
                        "youth_in_high_poverty_area",
                        type="hidden"
                    ),
                    HTML("""<hr>"""),
                    "subject_of_criminal_justice",
                    "arrest_record_employment_barrier",
                    "lacks_adequate_residence",
                    "irregular_sleep_accomodation",
                    "migratory_child",
                    "runaway_youth"
                )
            )
        )

    class Meta:
        model = WIOA
        fields = (
            "single_parent",
            "rural_area",
            "displaced_homemaker",
            "dislocated_worker",
            "cult_barriers_hind_emp",
            "in_foster_care",
            "aged_out_foster_care",
            "exhaust_tanf",
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
        )


class WioaForm(ModelForm):

    def clean_SID(self):
        data = self.cleaned_data['SID']
        if data != "":
            if WIOA.objects.filter(SID=data).count() > 0:
                raise ValidationError("Sorry, we have this SSN in our records already. Please call 504-671-5434 to speak to a staff member.")
        return data

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
            raise ValidationError(
                _('Sorry, the State of Louisiana requires'
                    ' that we collect race/ethnicity data'),
                code=ethnicity
            )

    def __init__(self, *args, **kwargs):
        super(WioaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Field(
                "SID",
                data_mask="999-99-9999"
            ),
            Fieldset(
                "Educational Details",
                Row(
                    Field(
                        "highest_level_completed",
                        "school_location",
                        wrapper_class="col-md-4"
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
                "migrant_seasonal_status",
                "long_term_unemployed",
            ),
            Fieldset(
                "Services/Training Information",
                Field(
                    "adult_one_stop",
                    "youth_one_stop",
                    "voc_rehab",
                    "wagner_peyser",
                    "recieved_training",
                    "etp_name",
                    "etp_program",
                    "etp_CIP_Code",
                    "training_type_1",
                    "training_type_2",
                    "training_type_3",
                    type="hidden"
                ),
                Field(
                    "job_corps",
                    "youth_build",
                    "school_status",
                    required=True
                )
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
                        wrapper_class="col-md-6"
                    )
                ),
            ),
            Fieldset(
                "Disability Disclosure",
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
                    '<h5>Learning Disabilities</h5>'
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
                )
            ),
            Fieldset(
                "Additional Details",
                Row(
                    HTML("""<div class="col-md-8"><p>This information is
                         optional, however, sharing it with us can help
                         us to better understand the needs of our
                         student body and provide additional
                         programming and services for all of
                         our students.</p></div>"""),
                ),
                Row(
                    Column(
                        "single_parent",
                        "rural_area",
                        "displaced_homemaker",
                        "dislocated_worker",
                        "state_payed_foster",
                        css_class="col-md-4"
                    ),
                    Column(
                        "cult_barriers_hind_emp",
                        "in_foster_care",
                        "aged_out_foster_care",
                        "exhaust_tanf",
                        css_class="col-md-4"
                    ),
                ),
                HTML("""<hr>"""),
                "recieves_public_assistance",
                Row(
                    Column(
                        HTML(
                            """<p>(i) SNAP or Louisiana Purchase Card </p>
                            <p>(ii) TANF Assistance</p>
                            <p>(iii) SSI Assistance</p>"""
                        ),
                        css_class="col-md-4"
                    ),
                    Column(
                        HTML(
                            """<p>(iv) State or local income-based public
                             assistance (Louisiana Medicaid, Section 8 Housing,
                             Kinship Care, Child Care Assisstance,
                             LSU Hospital Free Care, Free Dental Program)</p>"""
                        ),
                        css_class="col-md-4"
                    ),
                ),
                HTML("""<hr>"""),
                Field(
                    "low_family_income",
                    HTML("""<table class="table table-condensed">
                        <tr>
                        <th>Individual</th><th>Family of 2</th>
                        <th>Family of 3</th><th>Family of 4</th>
                        <th>Family of 5</th><th>Family of 6</th>
                        <th>Family of 7</th><th>Family of 8</th>
                        </tr>
                        <tr>
                        <td>$11,880</td><td>$16,020</td><td>$20,300</td>
                        <td>$25,062</td><td>$29,579</td><td>$34,595</td>
                        <td>$36,730</td><td>$40,890</td>
                        </tr></table>"""
                         ),
                    Field(
                        "disabled_in_poverty",
                        "youth_in_high_poverty_area",
                        type="hidden"
                    ),
                    HTML("""<hr>"""),
                    "subject_of_criminal_justice",
                    "arrest_record_employment_barrier",
                    "lacks_adequate_residence",
                    "irregular_sleep_accomodation",
                    "migratory_child",
                    "runaway_youth"
                )
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
        labels = {
            "recieves_public_assistance": "Please check this box if you receive assistance through any of the following programs.",
            "state_payed_foster": "Are you in state-payed foster care?",
            "subject_of_criminal_justice": "Have you ever been involved in the criminal justice system for committing a status offense or delinquent act?",
            "arrest_record_employment_barrier": "Do you need help overcoming employment barriers due to a criminal record?",
            "low_family_income": "Please check this box if you have low family income. See chart below for low income levels for families of various sizes",
            "lacks_adequate_residence": "Do you lack a fixed, regular, and adequate nighttime residence?",
            "irregular_sleep_accomodation": "Do you have irregular sleep accommodations?",
            "migratory_child": "Are you a migratory child?",
            "runaway_youth": "Are you a runaway youth?"        
        }


class StaffForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)
        self.fields['phone'].validators.append(phone_validator)
        self.fields['alt_phone'].validators.append(phone_validator)
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
                    'contact_preference',
                    wrapper_class="col-md-4"
                ),
            ),
            Row(
                Field(
                    'dob',
                    placeholder="MM/DD/YYYY",
                    data_mask="99/99/9999",
                    wrapper_class="col-md-6",
                    required=True
                ),
                Field(
                    'primary_language',
                    wrapper_class="col-md-6",
                    required=True
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
            'for_credit'
        )

    class Meta:
        model = Prospect
        fields = (
            'active',
            'duplicate',
            'for_credit'
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
            'notes'
        )

    class Meta:
        model = ProspectNote
        fields = (
            'contact_date',
            'contact_method',
            'successful',
            'notes'
        )



