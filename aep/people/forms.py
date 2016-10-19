from django.contrib.auth.models import User
from django.forms import ModelForm
from django.core.validators import RegexValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Submit, Row, Column, HTML, Div
from crispy_forms.bootstrap import PrependedText
from core.forms import NoColonModelForm
from .models import Student, Staff, WIOA


# Fields for the people forms

personal_fields = ('phone', 'alt_phone', 'dob')
address_fields = ('street_address_1', 'street_address_2', 'city', 'state')
emergency_contact_fields = ('emergency_contact', 'ec_phone', 'ec_email',)

people_fields = personal_fields + address_fields + emergency_contact_fields
student_fields = ('US_citizen', 'gender', 'marital_status')
staff_fields = ('bio',)

def make_username(first_name, last_name):
    if len(last_name) < 5:
        name = "{0}{1}".format(first_name[0], last_name).lower()
    else:
        name = "{0}{1}".format(first_name[0], last_name[:5]).lower()
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

    def save(self):
        user = super(UserForm, self).save(commit=False)
        user.username = make_username(user.first_name, user.last_name)
        user.password = User.objects.make_random_password()
        user.save()
        return user

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            Fieldset(
                'User Info',
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


class StudentForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.fields['phone'].validators.append(phone_validator)
        self.fields['alt_phone'].validators.append(phone_validator)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Fieldset(
                'Personal Info',
                Row(
                    Field(
                        'dob',
                        placeholder="MM/DD/YYYY",
                        wrapper_class="col-md-4"
                    ),
                    Field(
                        'gender',
                        'marital_status',
                        wrapper_class="col-md-4",
                    ),
                ),
                'other_ID',
                'US_citizen',
            ),
            Fieldset(
                'Contact Info',
                Row(
                    Field(
                        'phone',
                        placeholder="504-555-5555",
                        wrapper_class="col-md-6",
                        required=True
                    ),
                    Field(
                        'alt_phone',
                        wrapper_class="col-md-6"
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
                        'zip_code',
                        wrapper_class="col-md-4",
                        required=True
                    ),
                ),
                'parish',
            ),
            Fieldset(
                'Emergency Contact Info',
                'emergency_contact',
                'ec_phone',
                'ec_email',
                'ec_relation'
            ),
            Fieldset(
                'What types of classes are you interested in taking with us?',
                'ccr_app',
                'esl_app',
                'ace_app',
                'e_learn_app',
                'success_app'
            )
        )

    class Meta:
        model = Student
        fields = (
            "dob",
            "gender",
            "marital_status",
            "US_citizen",
            "other_ID",
            "ccr_app",
            "esl_app",
            "ace_app",
            "e_learn_app",
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
            "ec_relation",
        )

class WioaForm(NoColonModelForm):

    def __init__(self, *args, **kwargs):
        super(WioaForm, self).__init__(*args, **kwargs)
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
                "Services/Training",
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
                "job_corps",
                "youth_build",
                "school_status",
            ),
            Fieldset(
                'Race/Ethnicity/Language',
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
                            """ <p>(iv) State or local income-based public assistance (Louisiana Medicaid, Section 8 Housing, Kinship Care, Child Care Assisstance, LSU Hospital Free Care, Free Dental Program)</p>"""
                        ),
                        css_class="col-md-4"
                    ),
                ),
                Field(
                    "low_family_income",
                    HTML("""<table class="table table-condensed"><tr><th>Individual</th><th>Family of 2</th>
                        <th>Family of 3</th><th>Family of 4</th><th>Family of 5</th><th>Family of 6</th>
                        <th>Family of 7</th><th>Family of 8</th></tr><tr></tr><td>$11,880</td><td>$16,020</td><td>$20,300</td>
                        <td>$25,062</td><td>$29,579</td><td>$34,595</td><td>$36,730</td><td>$40,890</td></table>"""
                    ),
                    Field(
                        "disabled_in_poverty",
                        "youth_in_high_poverty_area",
                        type="hidden"
                    ),
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
            "native_language"
        )
        labels = {
            "recieves_public_assistance": "Please check this box if any of the following are true.",
            "state_payed_foster": "Are you in state-payed foster care?",
            "subject_of_criminal_justice": "Have you ever been involved in the criminal justice system for committing a status offense or delinquent act?",
            "arrest_record_employment_barrier": "Do you need help overcoming employment barriers due to criminal record?"
        }



class StaffForm(NoColonModelForm):
    class Meta:
        model = Staff
        fields = people_fields + staff_fields
