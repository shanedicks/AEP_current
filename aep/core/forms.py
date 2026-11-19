from datetime import date
from django.forms import ModelForm, Form, DateField, FileField, ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

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
        required=False
    )
    to_date = DateField(
        input_formats=[
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m/%d/%y'
        ],
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(DateFilterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = False
        self.helper.disable_csrf = True

def five_years_ago():
    today = date.today()
    try:
        return today.replace(year=today.year - 5)
    except ValueError:
        return today.replace(year=today.year - 5, day=28)


class CutoffDateForm(Form):

    cutoff = DateField(
        input_formats=[
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m/%d/%y'
        ],
        initial=five_years_ago
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = False
        self.helper.disable_csrf = True

class CSVImportForm(Form):

    csv_file = FileField()


    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')

        if csv_file:
            file_name = csv_file.name
            if not file_name.endswith('.csv'):
                raise ValidationError('Sorry, please provide a CSV file.')

        return csv_file

    def __init__(self, *args, **kwargs):
        super(CSVImportForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = False
        self.helper.form_show_labels = False
        self.helper.layour = Layout(
            'csv_file'
        )
