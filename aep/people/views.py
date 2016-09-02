from django.views.generic import DetailView, ListView, UpdateView, CreateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render 
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from .models import Staff, Student
from .forms import StaffForm, StudentForm, UserForm


class UserCreateView(CreateView):
    model = User
    form_class = UserForm
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

    def get_context_data(self, **kwargs):
        context = super(StudentCreateView, self).get_context_data(**kwargs)
        context['user_form'] = UserForm
        context.update(kwargs)
        return context


    def post(self, request, *args, **kwargs):
        user_form = UserForm(request.POST)
        student_form = StudentForm(request.POST)
        uf_valid = user_form.is_valid()
        sf_valid = student_form.is_valid()
        if uf_valid and sf_valid:
            user = user_form.save()
            student = student_form.save(commit=False)
            student.user = user
            student.save()
            self.object = student
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data())


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

    def get_context_data(self, **kwargs):
        context = super(StudentCreateView, self).get_context_data(**kwargs)
        context['user_form'] = UserForm
        context.update(kwargs)
        return context
