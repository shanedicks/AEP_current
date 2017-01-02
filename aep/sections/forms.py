from django.forms import ModelForm, Form, ChoiceField
from django.db.models import Q
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from people.models import Student
from .models import Enrollment, Section, Attendance


class StudentAddEnrollmentForm(ModelForm):

    def __init__(self, *args, **kwargs):
        name = kwargs.pop('name', None)
        qst = Student.objects.none()
        if name:
            name = name[0]
            qst = Student.objects.filter(
                Q(user__first_name__icontains=name) | Q(user__last_name__icontains=name)
            )
        self.base_fields['student'].queryset = qst
        super(StudentAddEnrollmentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Enrollment
        fields = ('student',)


class ClassAddEnrollmentForm(ModelForm):

    def __init__(self, *args, **kwargs):
        site = kwargs.pop('site', None)
        program = kwargs.pop('program', None)
        qst = Section.objects.all().order_by('site', 'title', 'start_time')
        if site and site[0] != '':
            qst = qst.filter(site=site[0])
        if program and program[0] != '':
            qst = qst.filter(program=program[0])
        self.base_fields['section'].queryset = qst
        super(ClassAddEnrollmentForm, self).__init__(*args, **kwargs)


class ClassAddFromListEnrollForm(ModelForm):

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk', None)
        super(ClassAddFromListEnrollForm, self).__init__(*args, **kwargs)
        if pk:
            pk = pk[0]
            self.fields['section'].queryset = Section.Objects.filter(pk=pk)

    class Meta:
        model = Enrollment
        fields = ('section',)


class SectionFilterForm(Form):

    site = ChoiceField(
        choices=(
            ('', '-------'),
            ('CP', 'City Park'),
            ('MC', 'NOALC'),
            ('WB', 'West Bank'),
            ('JP', 'Jefferson Parish'),
            ('SC', 'Sidney Collier')
        ),
        required=False
    )
    program = ChoiceField(
        choices=(
            ('', '-------'),
            ('ESL', 'ESL'),
            ('CCR', 'CCR'),
            ('TRANS', 'Transitions')
        ),
        required=False
    )


class SingleAttendanceForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(SingleAttendanceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            Field(
                'attendance_type',
                'time_in',
                'time_out',
                wrapper_class="col-md-4",
                required=True
            )

        )

    class Meta:
        model = Attendance
        fields = ('attendance_type', 'time_in', 'time_out')
