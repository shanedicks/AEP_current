from django.views.generic import DetailView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Section, Enrollment


class ClassListView(LoginRequiredMixin, ListView):

    model = Section
    template_name = 'sections/class_list.html'


class ClassDetailView(LoginRequiredMixin, DetailView):

    model = Section
    template_name = 'sections/class_detail.html'


class EnrollStudentView(LoginRequiredMixin, CreateView):

    model = Enrollment
    template_name = 'sections/enroll_student.html'
    fields = ['student', 'status']
