from django.forms import Form, ModelMultipleChoiceField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from .models import Semester

class SemesterForm(Form):
    
    semesters = ModelMultipleChoiceField(queryset=Semester.objects.all())

    def __init__(self, *args, **kwargs):
        super(SemesterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = False
        self.helper.form_show_labels = False
        self.helper.disable_csrf = True 

