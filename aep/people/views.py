from django.views.generic import DetailView, ListView, UpdateView, CreateView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Staff, Student
from .forms import StaffForm, StudentForm


class UserCreateView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'people/create_user.html'


class StudentDetailView(LoginRequiredMixin, DetailView):

    model = Student


class StudentListView(LoginRequiredMixin, ListView):

    model = Student


class StudentUpdateView(LoginRequiredMixin, UpdateView):

    model = Student


class StudentCreateView(LoginRequiredMixin, CreateView):

    model = Student
    form_class = StudentForm
    template_name = 'people/create_student.html'


class StaffDetailView(LoginRequiredMixin, DetailView):

    model = Staff


class StaffListView(LoginRequiredMixin, ListView):

    model = Staff


class StaffUpdateView(LoginRequiredMixin, UpdateView):

    model = Staff


class StaffCreateView(LoginRequiredMixin, CreateView):

    model = Staff
    form_class = StaffForm
    template_name = 'people/create_staff.html'
