from django.views.generic import DetailView, ListView, UpdateView, CreateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Staff, Student


class StudentDetailView(LoginRequiredMixin, DetailView):

    model = Student


class StudentListView(LoginRequiredMixin, ListView):

    model = Student


class StudentUpdateView(LoginRequiredMixin, UpdateView):

    model = Student


class StudentCreateView(LoginRequiredMixin, CreateView):

    model = Student
    template_name = 'create_student.html'


class StaffDetailView(LoginRequiredMixin, DetailView):

    model = Staff


class StaffListView(LoginRequiredMixin, ListView):

    model = Staff


class StaffUpdateView(LoginRequiredMixin, UpdateView):

    model = Staff


class StaffCreateView(LoginRequiredMixin, CreateView):

    model = Staff
    template_name = 'create_staff.html'