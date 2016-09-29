from django.contrib.auth.models import User
from django.forms import ModelForm
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


class UserForm(ModelForm):

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email'
        )

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
        self.helper.layout = Layout(
            Fieldset(
                'User Info',
                Row(
                    Field(
                        'first_name',
                        'last_name',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                ),
                'email'
            )
        )


class StudentForm(ModelForm):

    class Meta:
        model = Student
        fields = (
            "dob",
            "gender",
            "marital_status",
            "US_citizen",
            "other_ID",
            "program",
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

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template_pack = 'bootstrap3'
        self.helper.layout = Layout(
            Fieldset(
                'Personal Info',
                Row(
                    Field(
                        'dob',
                        'gender',
                        'marital_status',
                        wrapper_class="col-md-4"
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
                        'alt_phone',
                        wrapper_class="col-md-6",
                        required=True
                    ),
                ),
                Row(
                    Field(
                        'street_address_1',
                        'street_address_2',
                        wrapper_class="col-md-6",
                        required=True),
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
            )
        )


class WioaForm(NoColonModelForm):

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
            "public_assistance",
            "rural_area",
            "displaced_homemaker",
            "dislocated_worker",
            "cult_barriers_hind_emp",
            "in_foster_care",
            "aged_out_foster_care",
            "exhaust_tanf",
            "disability_status",
            "job_corps",
            "youth_build",
            "low_income",
            "low_literacy",
            "recieves_public_assistance",
            "low_family_income",
            "free_lunch_youth",
            "state_payed_foster",
            "disabled_in_poverty",
            "homeless",
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
            "highet_level_at_entry",
            "school_location",
            "country",
            "native_language"
        )

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
                        "highet_level_at_entry",
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
                "adult_one_stop",
                "youth_one_stop",
                "job_corps",
                "youth_build",
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
                Field("disability_status", type="hidden"),
                HTML('<h4>Physical Disabilities</h4>'),
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
                HTML('<h4>Learning Disabilities</h4>'),
                Row(
                    Column(
                        "dyscalculia",
                        css_class="col-md-3",
                    ),
                    Column(
                        "dysgraphia",
                        css_class="col-md-3",
                    ),
                    Column(
                        "dyslexia",
                        css_class="col-md-3",
                    ),
                    Column(
                        "neurological_impairments",
                        css_class="col-md-3",
                    ),
                ),
            ),
            Fieldset(
                "Additional Details",
                "single_parent",
                "public_assistance",
                "rural_area",
                "displaced_homemaker",
                "dislocated_worker",
                "cult_barriers_hind_emp",
                "in_foster_care",
                "aged_out_foster_care",
                "exhaust_tanf",
                "low_income",
                "low_literacy",
                "recieves_public_assistance",
                "low_family_income",
                "free_lunch_youth",
                "state_payed_foster",
                "disabled_in_poverty",
                "homeless",
                "youth_in_high_poverty_area",
                "subject_of_criminal_justice",
                "arrest_record_employment_barrier",
                "lacks_adequate_residence",
                "irregular_sleep_accomodation",
            ),
        )


class StaffForm(NoColonModelForm):
    class Meta:
        model = Staff
        fields = people_fields + staff_fields
