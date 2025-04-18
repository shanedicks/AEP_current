import datetime
from django.forms import (ModelForm, Form, ChoiceField, modelformset_factory,
                         ValidationError, CharField, DateField, TextInput, Select,
                         ModelChoiceField, ModelMultipleChoiceField)
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from core.forms import DateFilterForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from people.models import Student
from semesters.models import Semester
from academics.models import SkillMastery
from .models import Enrollment, Section, Attendance, Site, Cancellation


class StudentAddEnrollmentForm(ModelForm):

    STATUS_CHOICES = (
        ('A', 'Active'),
        ('W', 'Waitlist'),
    )

    def __init__(self, *args, **kwargs):
        student = kwargs.pop('student', None)
        qst = Student.objects.none()
        if student:
            student = student[0]
            qst = Student.objects.filter(
                Q(first_name__icontains=student) | Q(last_name__icontains=student) | Q(WRU_ID__icontains=student),
                duplicate=False
            )
        self.base_fields['student'].queryset = qst
        super(StudentAddEnrollmentForm, self).__init__(*args, **kwargs)
        self.fields['status'].choices = self.STATUS_CHOICES

    class Meta:
        model = Enrollment
        fields = ('student', 'status')


class ClassAddEnrollmentForm(ModelForm):

    STATUS_CHOICES = (
        ('A', 'Active'),
        ('W', 'Waitlist'),
    )

    def __init__(self, *args, **kwargs):
        site = kwargs.pop('site', None)
        program = kwargs.pop('program', None)
        days = kwargs.pop('days', None)
        limit = timezone.now() - datetime.timedelta(days=14)
        ell_limit = timezone.now() - datetime.timedelta(days=42)
        qst = Section.objects.filter(
            semester__start_date__gte=limit
        ) | Section.objects.filter(
            starting__gte=limit
        ) | Section.objects.filter(
            semester__start_date__gte=ell_limit,
            program='ELL'
        ) | Section.objects.filter(
            starting__gte=ell_limit,
            program='ELL'
        )
        if site and site[0] != '':
            qst = qst.filter(site=site[0])
        if program and program[0] != '':
            qst = qst.filter(program=program[0])
        if days and days[0] != '':
            qst = qst.filter(**{days[0]: True})
        qst = qst.exclude(closed=True)
        qst = qst.order_by('site', 'title', 'start_time')
        self.base_fields['section'].queryset = qst
        self.base_fields['section'].empty_label = "Section"
        super(ClassAddEnrollmentForm, self).__init__(*args, **kwargs)
        self.fields['status'].choices = self.STATUS_CHOICES
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = False
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Field('section'),
            Field('status')
        )

    def clean(self):
        data = super(ClassAddEnrollmentForm, self).clean()
        section = data.get('section')
        status = data.get('status')

        if section.is_full:
            if section.over_full:
                raise ValidationError(
                    _('Sorry, even the waitlist for this class is full. Please try something else'),
                    code='over full class'
                )
            if status == Enrollment.ACTIVE:
                raise ValidationError(
                    _('Sorry, this class is full. Please choose another, or change enrollment status from "Active" to "Waitlist'),
                    code='full class'
                )

    class Meta:
        model = Enrollment
        fields = ('section', 'status')


class SectionFilterForm(Form):

    site = ModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        empty_label='Site'
    )
    program = ChoiceField(
        choices=(
            ('', 'Program'),
            ('ELL', 'ELL'),
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


class SectionFilterFormWithDays(SectionFilterForm):
    days = ChoiceField(
        choices=(
            ('', 'Day'),
            ('monday', 'Monday'),
            ('tuesday', 'Tuesday'),
            ('wednesday', 'Wednesday'),
            ('thursday', 'Thursday'),
            ('friday', 'Friday'),
            ('saturday', 'Saturday'),
            ('sunday', 'Sunday'),
        ),
        required=False
    )


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


class SelectSemesterForm(Form):

    semesters = ModelMultipleChoiceField(queryset=Semester.objects.all())

    def __init__(self, *args, **kwargs):
        super(SelectSemesterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Field(
                'semesters'
            )
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
            ('ELL', 'ELL'),
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
                required=True,
            )
        )

    class Meta:
        model = Attendance
        fields = ('attendance_type', 'time_in', 'time_out')


AttendanceFormset = modelformset_factory(Attendance, form=SingleAttendanceForm, extra=0)


class SingleHoursAttendanceForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(SingleHoursAttendanceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            Field(
                'att_hours',
                wrapper_class="col-md-6",
            )
        )

    class Meta:
        model = Attendance
        fields = ('att_hours',)

        labels = {
            'att_hours': "Hours"
        }


HoursAttendanceFormset = modelformset_factory(Attendance, form=SingleHoursAttendanceForm, extra=0)

class AdminAttendanceForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(AdminAttendanceForm, self).__init__(*args, **kwargs)
        self.fields['attendance_date'].initial = timezone.now().date()
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


class EnrollmentUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(EnrollmentUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            Field(
                'status'
            )
        )

    class Meta:
        model = Enrollment
        fields = ('status',)

        labels = {
            'status': 'Enrollment Status'
        }


class CancellationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            Field(
                'cancellation_date',
                'send_notification'
            )
        )

    class Meta:
        model = Cancellation
        fields = ('cancellation_date', 'send_notification')
        widgets = {
            "cancellation_date": TextInput(attrs={'type': 'date'})
        }
