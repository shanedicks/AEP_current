from django.forms import ModelForm
from .models import Enrollment

class StudentAddEnrolmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ('student', 'status')

class ClassAddEnrollementForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ('section','status')   
