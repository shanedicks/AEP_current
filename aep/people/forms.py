from django.forms import ModelForm
from .models import Student, Staff

personal_fields = ('phone', 'alt_phone', 'dob')
address_fields = ('street_address_1', 'street_address_2', 'city', 'state')
emergency_contact_fields = ('emergency_contact', 'ec_phone', 'ec_email')

people_fields = personal_fields + address_fields + emergency_contact_fields

student_fields = ('intake_date', 'WRU_ID')

staff_fields = ('bio',)


class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = people_fields + student_fields


class StaffForm(ModelForm):
    class Meta:
        model = Staff
        fields = people_fields + staff_fields
