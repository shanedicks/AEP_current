import datetime
from django.db.models import Q
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset
from .models import TestAppointment, TestEvent


class TestAppointmentForm(ModelForm):
    class Meta:
        model = TestAppointment
        fields = ('student', 'event')


class TestSignupForm(ModelForm):
    class Meta:
        model = TestAppointment
        fields = ('event',)

    def __init__(self, *args, **kwargs):
        super(TestSignupForm, self).__init__(*args, **kwargs)
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


class PretestSignupForm(TestSignupForm):

    prefix = 'pretest'

    def __init__(self, *args, **kwargs):
        super(PretestSignupForm, self).__init__(*args, **kwargs)
        limit = datetime.datetime.today() + datetime.timedelta(days=2) # we only want test events at least 3 days away
        events = TestEvent.objects.filter(
            Q(test='TABE') | Q(test='CLAS-E'),
            start__date__gte=limit
        ).exclude(
            full=True
        ).order_by('start')
        self.fields['event'].queryset = events
        self.helper.layout = Layout(
            Fieldset(
                'Pre-Test Group',
                'event'
            )
        )


class LocatorSignupForm(TestSignupForm):

    prefix = 'locator'

    def __init__(self, *args, **kwargs):
        super(LocatorSignupForm, self).__init__(*args, **kwargs)
        limit = datetime.datetime.today() + datetime.timedelta(days=2) # we only want test events at least 3 days away
        events = TestEvent.objects.filter(
            Q(test='TABE Locator') | Q(test='CLAS-E Locator'),
            start__date__gte=limit
        ).exclude(
            full=True
        ).order_by('start')
        self.fields['event'].queryset = events
        self.helper.layout = Layout(
            Fieldset(
                'Orientation/Locator Group',
                'event'
            )
        )
