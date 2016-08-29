from django.forms import ModelForm, HiddenInput
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .models import Student, Staff


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password')
        success_url = reverse_lazy('people home')

# Fields for the people forms

personal_fields = ('user', 'phone', 'alt_phone', 'dob')
address_fields = ('street_address_1', 'street_address_2', 'city', 'state')
emergency_contact_fields = ('emergency_contact', 'ec_phone', 'ec_email')

people_fields = personal_fields + address_fields + emergency_contact_fields

student_fields = ('intake_date', 'WRU_ID')

staff_fields = ('bio',)


class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = people_fields + student_fields
        widgets = {'user': HiddenInput}


class StaffForm(ModelForm):
    class Meta:
        model = Staff
        fields = people_fields + staff_fields
        widgets = {'user': HiddenInput}
