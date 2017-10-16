from django.forms import ModelForm, Form, DateField
from crispy_forms.helper import FormHelper

class NoColonModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super(NoColonModelForm, self).__init__(*args, **kwargs)


class DateFilterForm(Form):

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

    def __init__(self, *args, **kwargs):
        super(DateFilterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = False
        self.helper.disable_csrf = True