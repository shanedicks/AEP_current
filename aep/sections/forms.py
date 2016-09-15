from django.forms import ModelForm
from .models import Enrollment

class StudentToClassEnrollForm(forms.ModelForm):

    model = Enrollment
    fields = ('student' 'status')
