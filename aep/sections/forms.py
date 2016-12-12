from django.forms import ModelForm, Form, ChoiceField
from django.db.models import Q
from people.models import Student
from .models import Enrollment, Section


class StudentAddEnrolmentForm(ModelForm):

    def __init__(self, *args, **kwargs):
        f_name = kwargs.pop('f_name', None)
        l_name = kwargs.pop('l_name', None)
        qst = Student.objects.none()
        if f_name or l_name:
            qst = Student.objects.filter(
                Q(user__first_name__icontains=f_name) | Q(user__first_name__icontains=f_name)
            )
        return qst

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

    class Meta:
        model = Enrollment
        fields = ('section',)


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
