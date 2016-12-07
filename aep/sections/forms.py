from django.forms import ModelForm, Form, ChoiceField
from .models import Enrollment, Section


class StudentAddEnrolmentForm(ModelForm):
    class Meta:
        model = Enrollment
        fields = ('student',)


class ClassAddEnrollmentForm(ModelForm):

    class Meta:
        model = Enrollment
        fields = ('section',)


class ClassAddFromListEnrollForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ClassAddFromListEnrollForm, self).__init__(*args, **kwargs)
        pk = kwargs.pop('pk', None)
        if pk:
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
