import datetime
from django.db.models import Q
from django.forms import ModelForm, Form, FileField, modelformset_factory
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset
from .models import (TestEvent, TestAppointment,
                     Tabe, Clas_E, HiSet_Practice, Gain)

class CSVImportForm(Form):
    csv_file = FileField()

    def __init__(self, *args, **kwargs):
        super(CSVImportForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = False
        self.helper.form_show_labels = False
        self.helper.layour = Layout(
            'csv_file'
        )

class TestAppointmentForm(ModelForm):
    class Meta:
        model = TestAppointment
        fields = ('student', 'event')


class TestAppointmentAttendanceForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(TestAppointmentAttendanceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            Field(
                'attendance_type',
                wrapper_class="col-md-4",
                required=True
            ),
            Field(
                'time_in',
                'time_out',
                wrapper_class="col-md-4"
            )
        )

    class Meta:
        model = TestAppointment
        fields = ('attendance_type', 'time_in', 'time_out')


class TestSignupForm(ModelForm):
    class Meta:
        model = TestAppointment
        fields = ('event', 'notes')

    def __init__(self, *args, **kwargs):
        super(TestSignupForm, self).__init__(*args, **kwargs)
        limit = datetime.datetime.today()
        events = TestEvent.objects.filter(
            start__date__gte=limit
        ).order_by('title')
        self.fields['event'].queryset = events
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = False
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Fieldset(
                'Testing Group',
                'event',
                'notes'
            )
        )


class OrientationSignupForm(TestSignupForm):

    prefix = 'orientation'

    class Meta:
        model = TestAppointment
        fields = ('event',)

    def __init__(self, *args, **kwargs):
        super(OrientationSignupForm, self).__init__(*args, **kwargs)
        limit = datetime.datetime.today() + datetime.timedelta(days=2) # we only want test events at least 2 days away
        events = TestEvent.objects.filter(
            test='Orientation',
            start__date__gte=limit
        ).exclude(
            full=True
        ).order_by('title')
        self.fields['event'].queryset = events
        self.helper.layout = Layout(
            Fieldset(
                'Orientation Sign-up',
                'event'
            )
        )


class TabeForm(ModelForm):

    class Meta:
        model = Tabe
        fields = (
            'test_date',
            'form',
            'read_level',
            'math_level',
            'lang_level',
            'read_ss',
            'math_comp_ss',
            'app_math_ss',
            'lang_ss',
            'total_math_ss',
            'total_batt_ss',
            'read_ge',
            'math_comp_ge',
            'app_math_ge',
            'lang_ge',
            'total_math_ge',
            'total_batt_ge',
            'read_nrs',
            'math_nrs',
            'lang_nrs',
        )

    def __init__(self, *args, **kwargs):
        super(TabeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = False
        self.helper.layout = Layout(
            Field(
                'test_date',
                placeholder="MM/DD/YYYY",
                data_mask="99/99/9999"
            ),
            Fieldset(
                'Form and Level Info',
                Field(
                    'form',
                    'read_level',
                    'math_level',
                    'lang_level',
                    wrapper_class='col-md-3'
                ),
            ),
            Fieldset(
                'Scale Score',
                Field(
                    'read_ss',
                    'math_comp_ss',
                    'app_math_ss',
                    'lang_ss',
                    'total_math_ss',
                    'total_batt_ss',
                    wrapper_class='col-md-2'
                ),
            ),
            Fieldset(
                'Grade Equivalency',
                Field(
                    'read_ge',
                    'math_comp_ge',
                    'app_math_ge',
                    'lang_ge',
                    'total_math_ge',
                    'total_batt_ge',
                    wrapper_class='col-md-4'
                ),
            ),
            Fieldset(
                'NRS Levels',
                Field(
                    'read_nrs',
                    'math_nrs',
                    'lang_nrs',
                    wrapper_class='col-md-4'
                )
            )
        )


class Clas_E_Form(ModelForm):

    class Meta:
        model = Clas_E
        fields = (
            'test_date',
            'form',
            'read_level',
            'read_ss',
            'read_nrs'
        )

    def __init__(self, *args, **kwargs):
        super(Clas_E_Form, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = False
        self.helper.layout = Layout(
            Field(
                'test_date',
                placeholder="MM/DD/YYYY",
                data_mask="99/99/9999"
            ),
            Field(
                'form',
                'read_level',
                'read_ss',
                'read_nrs',
                wrapper_class='col-md-3'
            )
        )


class GainForm(ModelForm):

    class Meta:
        model = Gain
        fields = (
            'test_date',
            'form',
            'subject',
            'scale_score',
            'nrs',
            'grade_eq'
        )

    def __init__(self, *args, **kwargs):
        super(GainForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = False
        self.helper.layout = Layout(
            Field(
                'test_date',
                placeholder="MM/DD/YYYY",
                data_mask="99/99/9999"
            ),
            Field(
                'form',
                'subject',
                wrapper_class='col-md-6'
            ),
            Field(
                'scale_score',
                'nrs',
                'grade_eq',
                wrapper_class='col-md-4'
            ),
        )


class HiSet_Practice_Form(ModelForm):

    class Meta:
        model = HiSet_Practice
        fields = (
            'test_date',
            'subject',
            'proctor',
            'test_version',
            'score',
            'grade'
        )

    def __init__(self, *args, **kwargs):
        super(HiSet_Practice_Form, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = False
        self.helper.layout = Layout(
            Field(
                'test_date',
                placeholder="MM/DD/YYYY",
                data_mask="99/99/9999"
            ),
            Field(
                'proctor',
                'test_version',
                wrapper_class='col-md-6'
            ),
            Field(
                'subject',
                'score',
                'grade',
                wrapper_class='col-md-4'
            )
        )

TestAttendanceFormSet = modelformset_factory(
        TestAppointment, 
        form=TestAppointmentAttendanceForm, 
        extra=0
    )
