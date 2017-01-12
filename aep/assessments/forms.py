import datetime
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset
from .models import TestAppointment, TestEvent


class TestAppointmentForm(ModelForm):
    class Meta:
        model = TestAppointment
        fields = ('student', 'event')


class PretestSignupForm(ModelForm):
    class Meta:
        model = TestAppointment
        fields = ('event',)

    def __init__(self, *args, **kwargs):
        limit = datetime.datetime.today() + datetime.timedelta(days=3) # we only want test events at least 3 days away
        events = TestEvent.objects.filter(
            start__date__gte=limit
        ).exclude(
            full=True
        ).order_by('start')
        self.base_fields['event'].queryset = events
        super(PretestSignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.help_text_inline = False
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Fieldset(
                'Testing Group',
                'event'
            )
        )
