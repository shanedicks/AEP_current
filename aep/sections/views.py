from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Section


class ClassListView(LoginRequiredMixin, ListView):

    model = Section
    template_name = 'sections/class_list.html'


class ClassDetailView(LoginRequiredMixin, DetailView):

    model = Section
    template_name = 'sections/class_detail.html'
