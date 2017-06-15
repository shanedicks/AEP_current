from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import (
    DetailView, ListView, UpdateView,
    CreateView, TemplateView, FormView)
from people.models import Student
from .models import Profile, Coaching, MeetingNote, AceRecord, ElearnRecord
from .forms import (
    ProfileForm, MeetingNoteForm,
    AssignCoach, AceRecordForm, ElearnRecordForm)


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

    def get_context_data(self, **kwargs):
        context = super(CoachingDetailView, self).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = self.object.coachee
            context.update(kwargs)
        return context


class MeetingNoteCreateView(LoginRequiredMixin, CreateView):

    model = MeetingNote
    form_class = MeetingNoteForm
    template_name = 'coaching/meeting_note_form.html'

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
    form_class = MeetingNoteForm
    template_name = 'coaching/meeting_note_form.html'

    def get_success_url(self):
        coaching = self.object.coaching
        return reverse_lazy(
            'coaching:coaching detail',
            kwargs={'pk': coaching.pk}
        )


class AceRecordCreateView(LoginRequiredMixin, CreateView):

    model = AceRecord
    form_class = AceRecordForm
    template_name = 'coaching/create_ace_record.html'

    def get_context_data(self, **kwargs):
        context = super(AceRecordCreateView, self).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context

    def form_valid(self, form):
        ace = form.save(commit=False)
        student = Student.objects.get(slug=self.kwargs['slug'])
        ace.student = student
        ace.save()
        return super(AceRecordCreateView, self).form_valid(form)


class AceRecordDetailView(LoginRequiredMixin, DetailView):

    model = AceRecord
    context_object_name = 'record'
    template_name = 'coaching/ace_record_detail.html'

    def get(self, request, *args, **kwargs):
        try:
            self.object = AceRecord.objects.get(student__slug=kwargs['slug'])
        except AceRecord.DoesNotExist:
            raise Http404('Student has no Ace Record, please create one.')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(AceRecordDetailView, self).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context


class AceRecordListView(LoginRequiredMixin, ListView):

    model = AceRecord
    template_name = 'coaching/ace_record_list.html'
    context_object_name = 'records'


class AceRecordCSV(LoginRequiredMixin, FormView):

    model = AceRecord


class ElearnRecordCreateView(LoginRequiredMixin, CreateView):

    model = ElearnRecord
    form_class = ElearnRecordForm
    template_name = 'coaching/create_elearn_record.html'

    def get_context_data(self, **kwargs):
        context = super(ElearnRecordCreateView, self).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context

    def form_valid(self, form):
        record = form.save(commit=False)
        student = Student.objects.get(slug=self.kwargs['slug'])
        record.student = student
        record.save()
        return super(ElearnRecordCreateView, self).form_valid(form)


class ElearnRecordDetailView(LoginRequiredMixin, DetailView):

    model = ElearnRecord

    def get(self, request, *args, **kwargs):
        try:
            self.object = ElearnRecord.objects.get(student__slug=kwargs['slug'])
        except ElearnRecord.DoesNotExist:
            raise Http404('Student has no eLearn Record, please create one.')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(ElearnRecordDetailView, self).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context


class ElearnRecordListView(LoginRequiredMixin, ListView):

    model = ElearnRecord


class ElearnRecordCSV(LoginRequiredMixin, FormView):

    model = ElearnRecord
