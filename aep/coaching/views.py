from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import (
    DetailView, ListView, UpdateView,
    CreateView, TemplateView, FormView)
from people.models import Student
from .models import Profile, Coaching, MeetingNote, AceRecord
from .forms import ProfileForm


class ProfileCreateView(LoginRequiredMixin, CreateView):

    model = Profile
    form_class = ProfileForm
    template_name = 'coaching/create_profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileCreateView, self).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context

    def form_valid(self, form):
        profile = form.save(commit=False)
        student = Student.objects.get(slug=self.kwargs['slug'])
        profile.student = student
        profile.save()
        return super(ProfileCreateView, self).form_valid(form)



class ProfileDetailView(LoginRequiredMixin, DetailView):

    model = Profile

    def get(self, request, *args, **kwargs):
        try:
            self.object = Profile.objects.get(student__slug=kwargs['slug'])
        except Profile.DoesNotExist:
            raise Http404('Student has no Coaching Profile, please create one.')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context


class CoachingCreateView(LoginRequiredMixin, CreateView):

    model = Coaching


class CoachingDetailView(LoginRequiredMixin, DetailView):

    model = Coaching


class MeetingNoteCreateView(LoginRequiredMixin, CreateView):

    model = MeetingNote


class MeetingNoteDetailView(LoginRequiredMixin, DetailView):

    model = MeetingNote


class AceRecordCreateView(LoginRequiredMixin, CreateView):

    model = AceRecord


class AceRecordDetailView(LoginRequiredMixin, DetailView):

    model = AceRecord
