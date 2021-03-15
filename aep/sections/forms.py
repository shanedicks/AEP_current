import datetime
from django.forms import (ModelForm, Form, ChoiceField, modelformset_factory,
                         ValidationError, CharField, DateField,
                         ModelChoiceField, ModelMultipleChoiceField)
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from core.forms import DateFilterForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from people.models import Student
from semesters.models import Semester
from academics.models import SkillMastery
from .models import Enrollment, Section, Attendance, Site


class StudentAddEnrollmentForm(ModelForm):

    def __init__(self, *args, **kwargs):
        name = kwargs.pop('name', None)
        qst = Student.objects.none()
        if name:
            name = name[0]
            qst = Student.objects.filter(
                Q(first_name__icontains=name) | Q(last_name__icontains=name) | Q(WRU_ID__icontains=name),
                duplicate=False
            )
        self.base_fields['student'].queryset = qst
        super(StudentAddEnrollmentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Enrollment
        fields = ('student',)


class ClassAddEnrollmentForm(ModelForm):

    STATUS_CHOICES = (
        ('A', 'Active'),
    )

    def __init__(self, *args, **kwargs):
        site = kwargs.pop('site', None)
        program = kwargs.pop('program', None)
        limit = datetime.datetime.today() - datetime.timedelta(days=7)
        qst = Section.objects.filter(
            semester__start_date__gte=limit
        ) | Section.objects.filter(
            starting__gte=limit
        )
        qst.order_by('site', 'title', 'start_time')
        if site and site[0] != '':
            qst = qst.filter(site=site[0])
        if program and program[0] != '':
            qst = qst.filter(program=program[0])
        self.base_fields['section'].queryset = qst
        self.base_fields['section'].empty_label = "Section"
        super(ClassAddEnrollmentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = False
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Field('section')
        )

    def clean(self):
        data = super(ClassAddEnrollmentForm, self).clean()
        section = data.get('section')

        if section.is_full:
            raise ValidationError(
                _('Sorry, this class is full. Please choose another'),
                code='full class'
            )

    class Meta:
        model = Enrollment
        fields = ('section',)


class SectionFilterForm(Form):

    site = ModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        empty_label='Site'
    )
    program = ChoiceField(
        choices=(
            ('', 'Program'),
            ('ESL', 'ESL'),
            ('CCR', 'CCR'),
            ('TRANS', 'Transitions'),
            ('ELRN', 'ELearn'),
            ('ADMIN', 'Admin'),
        ),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(SectionFilterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = False
        self.helper.form_show_labels = False
        self.helper.disable_csrf = True 


class EnrollmentReportForm(SectionFilterForm):

    semesters = ModelMultipleChoiceField(queryset=Semester.objects.all())


class AttendanceReportForm(Form):

    from_date = DateField(
        input_formats=[
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m/%d/%y'
        ],
        required=True
    )
    to_date = DateField(
        input_formats=[
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m/%d/%y'
        ],
        required=True
    )

    semesters = ModelMultipleChoiceField(queryset=Semester.objects.all())

    def __init__(self, *args, **kwargs):
        super(AttendanceReportForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Field(
                'semesters'
            ),
            Field(
                'from_date',
                'to_date'
            ),
        )


class SectionSearchForm(Form):

    c_name = CharField(label=_('Class Name'), required=False)

    site = ModelChoiceField(
        queryset=Site.objects.all(),
        empty_label='Site',
        required=False
    )

    program = ChoiceField(
        choices=(
            ('', 'Program'),
            ('ESL', 'ESL'),
            ('CCR', 'CCR'),
            ('TRANS', 'Transitions'),
            ('ELRN', 'ELearn'),
            ('ADMIN', 'Admin'),
        ),
        required=False
    )

    def filter_queryset(self, request, queryset):
        qst = queryset
        if self.cleaned_data['program']:
            qst = qst.filter(
                program=self.cleaned_data['program']
            )
        if self.cleaned_data['site']:
            qst = qst.filter(
                site=self.cleaned_data['site']
            )
        if self.cleaned_data['c_name']:
            qst = qst.filter(
                title__icontains=self.cleaned_data['c_name']
            )
        return qst

    def __init__(self, *args, **kwargs):
        super(SectionSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = False
        self.helper.disable_csrf = True
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Field('c_name', placeholder='Class Name'),
            Field(
                'site',
                'program'
            )
        )


class SingleAttendanceForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(SingleAttendanceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
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


AttendanceFormset = modelformset_factory(Attendance, form=SingleAttendanceForm, extra=0)


class AdminAttendanceForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(AdminAttendanceForm, self).__init__(*args, **kwargs)
        self.fields['attendance_date'].initial = datetime.datetime.today().date()
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field(
                'attendance_date',
                'att_hours',
                required=True
            )
        )

    class Meta:
        model = Attendance
        fields = ('attendance_date', 'att_hours')

        labels = {
            'attendance_date': "Date",
            'att_hours': "Hours"
        }


class SingleSkillMasteryForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(SingleSkillMasteryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            Field(
                'mastered',
                'cert_date',
                wrapper_class="col-md-4"
            )
        )

    class Meta:
        model = SkillMastery
        fields = ('cert_date', 'mastered')

        labels = {
            'cert_date': 'Date'
        }

SkillMasteryFormset = modelformset_factory(SkillMastery, form=SingleSkillMasteryForm, extra=0)
