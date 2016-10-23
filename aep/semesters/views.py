from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Semester


class SemesterListView(LoginRequiredMixin, ListView):

    model = Semester
    template_name = 'semesters/semester_list.html'


class SemesterDetailView(LoginRequiredMixin, DetailView):

    model = Semester
    template_name = 'semesters/semester_detail.html'
