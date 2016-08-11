from django.views.generic import DetailView, ListView, UpdateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Staff, Student


class StudentDetailView(LoginRequiredMixin, DetailView):

    model = Student


class StudentListView(LoginRequiredMixin, ListView):

    model = Student


class StudentUpdateView(LoginRequiredMixin, UpdateView):

    model = Student


class StaffDetailView(LoginRequiredMixin, DetailView):

    model = Staff


class StaffListView(LoginRequiredMixin, ListView):

    model = Staff


class StaffUpdateView(LoginRequiredMixin, UpdateView):

    model = Staff
