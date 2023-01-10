from django.apps import apps
from django.db.models import Q
from django.forms import ModelForm, TextInput
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Row, Column
from .models import Category, Item, Ticket


class SelectTicketItemForm(ModelForm):

    def __init__(self, *args, **kwargs):
        category = kwargs.pop('category', None)
        item_qst = Item.objects.all()
        if category:
            category = Category.objects.get(pk=category[0])
            item_qst = category.available()
        else:
            item_qst = Item.objects.exclude(
                tickets__issued_date__isnull=False,
                tickets__returned_date__isnull=True,
            )
        self.base_fields['item'].queryset = item_qst
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field(
                'item',
                'issued_date',
                wrapper_class="col-md-6"
            )
        )

    class Meta:
        model = Ticket
        fields = (
            'item',
            'issued_date'
        )
        widgets = {
            "issued_date": TextInput(attrs={'type': 'date'})
        }


class TicketForm(ModelForm):

    def clean(self):
        data = super().clean()
        person = [
            data['student'],
            data['staff']
        ]
        if not any(person):
            msg = _("Item must be assigned to either a student or staff member")
            self.add_error('student', msg)

    def __init__(self, *args, **kwargs):
        category = kwargs.pop('category', None)
        item_qst = Item.objects.all()
        if category:
            category = Category.objects.get(pk=category[0])
            item_qst = category.available()
        else:
            item_qst = Item.objects.exclude(
                tickets__issued_date__isnull=False,
                tickets__returned_date__isnull=True,
            )
        student = kwargs.pop('student', None)
        Student = apps.get_model('people', 'Student')
        student_qst = Student.objects.none()
        staff = kwargs.pop('staff', None)
        Staff = apps.get_model('people', 'Staff')
        staff_qst = Staff.objects.none()
        if student:
            student = student[0]
            student_qst = Student.objects.filter(
                Q(first_name__icontains=student) | Q(last_name__icontains=student) | Q(WRU_ID__icontains=student),
                duplicate=False
            )
        if staff:
            staff = staff[0]
            staff = Staff.objects.filter(
                Q(first_name__icontains=staff) | Q(last_name__icontains=staff),
            )
        self.base_fields['item'].queryset = item_qst
        self.base_fields['student'].queryset = student_qst
        self.base_fields['staff'].queryset = staff_qst
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'item',
            'student',
            'staff',
            'issued_date'
        )

    class Meta:
        model = Ticket
        fields = (
            'item',
            'student',
            'staff',
            'issued_date',
        )
        widgets = {
            "issued_date": TextInput(attrs={'type': 'date'})
        }
