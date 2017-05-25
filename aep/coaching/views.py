from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import (
    DetailView, ListView, UpdateView,
    CreateView, TemplateView, FormView)
from people.models import Student
from .models import Profile, Coaching, MeetingNote, AceRecord
from .forms import ProfileForm, MeetingNoteForm, AssignCoach


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


class CoacheeListView(LoginRequiredMixin, ListView):

    model = Coaching


class CoachingCreateView(LoginRequiredMixin, CreateView):

    model = Coaching
    form_class = AssignCoach
    template_name = 'coaching/create_coaching.html'

    def form_valid(self, form):
        coaching = form.save(commit=False)
        student = Student.objects.get(slug=self.kwargs['slug'])
        coaching.coachee = student
        coaching.save()
        return super(CoachingCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CoachingCreateView, self).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context


class CoachingDetailView(LoginRequiredMixin, DetailView):

    model = Coaching


class MeetingNoteCreateView(LoginRequiredMixin, CreateView):

    model = MeetingNote
    form_class = MeetingNoteForm
    template_name = 'coaching/create_meeting_note.html'

    def form_valid(self, form):
        note = form.save(commit=False)
        coaching = Coaching.objects.get(pk=self.kwargs['pk'])
        note.coaching = coaching
        note.save()
        return super(MeetingNoteCreateView, self).form_valid(form)

    def get_success_url(self):
        coaching = self.object.coaching
        return reverse_lazy(
            'coaching:coaching detail',
            kwargs={'pk': coaching.pk}
        )


class MeetingNoteDetailView(LoginRequiredMixin, DetailView):

    model = MeetingNote
    template_name = 'coaching/meeting_note_detail.html'
    context_object_name = 'note'


class MeetingNoteUpdateView(LoginRequiredMixin, UpdateView):

    model = MeetingNote


class AceRecordCreateView(LoginRequiredMixin, CreateView):

    model = AceRecord


class AceRecordDetailView(LoginRequiredMixin, DetailView):

    model = AceRecord
