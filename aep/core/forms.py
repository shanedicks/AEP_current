from django.forms import ModelForm

class NoColonModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label_suffix", "")
        super(NoColonModelForm, self).__init__(*args, **kwargs)