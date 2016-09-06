from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import Student, Staff


def make_username(first_name, last_name):
    if len(last_name) < 5:
        name = "{0}{1}".format(first_name[0], last_name).lower()
    else:
        name = "{0}{1}".format(first_name[0], last_name[:5]).lower()
    x = 0
    while True:
        if x == 0 and User.objects.filter(username=name).count() == 0:
            return name
        else:
            new_name = "{0}{1}".format(name, x)
            if User.objects.filter(username=new_name).count() == 0:
                return new_name
        x += 1


class UserForm(ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def save(self):
        user = super(UserForm, self).save(commit=False)
        user.username = make_username(user.first_name, user.last_name)
        user.password = User.objects.make_random_password()
        user.save()
        return user


# Fields for the people forms

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
