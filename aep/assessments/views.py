from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.urls import reverse
from django.views.generic import (DetailView, ListView, CreateView,
                                  DeleteView, UpdateView, TemplateView)

from people.models import Student
from .models import (TestEvent, TestAppointment, TestHistory,
                     Tabe, Clas_E, HiSet_Practice)
from .forms import TestSignupForm


class TestingHomeView(LoginRequiredMixin, TemplateView):

    template_name = 'assessments/testing_home.html'

class TestEventDetailView(LoginRequiredMixin, DetailView):

    model = TestEvent
    template_name = 'assessments/test_event_detail.html'
    context_object_name = "event"


class TestEventListView(LoginRequiredMixin, ListView):

    model = TestEvent
    template_name = "assessments/test_event_list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(
            TestEventListView,
            self
        ).get_context_data(*args, **kwargs)
        if 'upcoming' not in context:
            context['upcoming'] = TestEvent.objects.filter(
                start__gte=datetime.today()
            )
            context.update(kwargs)
        if 'past' not in context:
            context['past'] = TestEvent.objects.filter(
                start__lt=datetime.today()
            )
            context.update(kwargs)
        return context


class TestingSignupView(LoginRequiredMixin, CreateView):

    model = TestAppointment
    form_class = TestSignupForm
    template_name = 'assessments/test_signup.html'


    def get_context_data(self, **kwargs):
        context = super(
            TestingSignupView,
            self
        ).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context

    def form_valid(self, form):
        student = Student.objects.get(slug=self.kwargs['slug'])
        appt = form.save(commit=False)
        appt.student = student
        appt.save()
        return super(TestingSignupView, self).form_valid(form)


class TestAppointmentDetailView(LoginRequiredMixin, DetailView):

    model = TestAppointment
    template_name = 'assessments/test_appointment_detail.html'
    context_object_name = "appt"


class StudentTestHistoryView(LoginRequiredMixin, DetailView):

    model = TestHistory
    template_name = 'assessments/student_test_history.html'
    context_object_name = 'history'

    def get(self, request, *args, **kwargs):
        try:
            self.object = TestHistory.objects.get(student__slug=kwargs['slug'])
        except TestHistory.DoesNotExist:
            raise Http404('Student has no Test History, please ask a site leader to "Testify" them.')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(
            StudentTestHistoryView,
            self
        ).get_context_data(**kwargs)

        if 'appts' not in context:
            context['appts'] = TestAppointment.objects.filter(
                student__slug=self.kwargs['slug']
            ).order_by('event__start')
            context.update(kwargs)
        return context



class StudentTestListView(LoginRequiredMixin, ListView):

    class Meta:
        abstract = True

    def get_context_data(self, **kwargs):
        context = super(
            StudentTestListView,
            self
        ).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context


class StudentTestDetailView(LoginRequiredMixin, DetailView):

    class Meta:
        abstract = True

    def get_context_data(self, **kwargs):
        context = super(
            StudentTestDetailView,
            self
        ).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context


class StudentTabeListView(StudentTestListView):

    model = Tabe
    template_name = 'assessments/student_tabe_list.html'

    def get_queryset(self, **kwargs):
        qst = Tabe.objects.filter(student__student__slug=self.kwargs['slug'])
        return qst


class StudentTabeDetailView(StudentTestDetailView):

    model = Tabe
    template_name = 'assessments/student_tabe_detail.html'


class StudentClasEListView(StudentTestListView):

    model = Clas_E
    template_name = 'assessments/student_clas-e_list.html'


class StudentClasEDetailView(StudentTestDetailView):

    model = Clas_E
    template_name = 'assessments/student_clas-e_detail.html'


class StudentHisetPracticeListView(StudentTestListView):

    model = HiSet_Practice
    template_name = 'assessments/student_hiset_practice_list.html'


class StudentHisetPracticeDetailView(StudentTestDetailView):

    model = HiSet_Practice
    template_name = 'assessments/student_hiset_practice_detail.html'
