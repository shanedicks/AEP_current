from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse_lazy
from django.views.generic import (
    DetailView, ListView, UpdateView,
    CreateView, TemplateView, FormView)
from formtools.wizard.views import SessionWizardView
from core.forms import DateFilterForm
from core.utils import render_to_csv
from people.models import Student
from .models import Profile, Coaching, MeetingNote, AceRecord, ElearnRecord
from .forms import (
    ProfileForm, NewMeetingNoteForm,
    AssignCoach, AceRecordForm, ElearnRecordForm,
    AcademicQuestionaireForm, PersonalQuestionaireForm,
    GeneralInfoForm)
import rules

class StudentCoachingView(LoginRequiredMixin, DetailView):

    model = Student
    template_name = 'coaching/student_coaching.html'

class ProfileCreateWizard(LoginRequiredMixin, SessionWizardView):

    form_list = [
        GeneralInfoForm,
        AcademicQuestionaireForm,
        PersonalQuestionaireForm
    ]

    template_name = 'coaching/profile_wizard.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileCreateWizard, self).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context

    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()
        profile = Profile(**data)
        student = Student.objects.get(slug=self.kwargs['slug'])
        profile.student = student
        profile.save()
        return HttpResponseRedirect(
            reverse_lazy(
                'coaching:profile detail',
                kwargs={'slug': student.slug}
            )
        )


class ProfileUpdateWizard(LoginRequiredMixin, SessionWizardView):

    form_list = [
        GeneralInfoForm,
        AcademicQuestionaireForm,
        PersonalQuestionaireForm
    ]

    template_name = 'coaching/profile_wizard.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileUpdateWizard, self).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context

    def get_form_instance(self, step):
        return Profile.objects.get(student__slug=self.kwargs['slug'])

    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()
        student = Student.objects.get(slug=self.kwargs['slug'])
        profile = Profile.objects.filter(student=student).update(**data)
        return HttpResponseRedirect(
            reverse_lazy(
                'coaching:profile detail',
                kwargs={'slug': student.slug}
            )
        )


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


class CoacheeExportCSV(LoginRequiredMixin, ListView):
    model = Coaching

    def get_student_data(self, coachings):
        Attendance = apps.get_model('sections', 'Attendance')
        data = []
        headers = [
            'Last Name',
            'First Name',
            'Personal Email',
            'G Suite Email',
            'Phone',
            'Date of Last Note',
            'Last Note Content',
            'Date of Last Attendance',
            'Last Attendance Section',
            'Last Tabe',
            'Last Hiset Practice'
        ]
        data.append(headers)
        for coaching in coachings:
            try:
                last_note = coaching.notes.latest('meeting_date')
                last_note_date = last_note.meeting_date
                last_note_note = last_note.notes
            except ObjectDoesNotExist:
                last_note_date ="No notes found"
                last_note_note = ""
            try:
                attendance = Attendance.objects.filter(
                    enrollment__student=coaching.coachee,
                    attendance_type = 'P'
                )
                last_attendance = attendance.latest('attendance_date', 'time_in')
                last_attendance_date = last_attendance.attendance_date
                section = last_attendance.enrollment.section
            except ObjectDoesNotExist:
                last_attendance_date = "No attendance found"
                section = ""
            try:
                elearn_record = coaching.coachee.elearn_record
                if elearn_record.g_suite_email != '':
                    g_suite_email = elearn_record.g_suite_email
                else:
                    g_suite_email = 'Student has no g_suite_email'
            except ObjectDoesNotExist:
                g_suite_email = 'Student has no elearn_record'
            try:
                tests = coaching.coachee.tests
                try:
                    last_tabe = tests.latest_tabe.test_date
                except ObjectDoesNotExist:
                    last_tabe = 'Student has no TABE'
                try:
                    last_hiset = tests.latest_hiset_practice[0].test_date
                except ObjectDoesNotExist:
                    last_hiset = 'Student has no Practice Test'
            except ObjectDoesNotExist:
                last_tabe = 'Student has no Test History'
                last_hiset = 'Student has no Test History'

            s = [
                coaching.coachee.last_name,
                coaching.coachee.first_name,
                coaching.coachee.email,
                g_suite_email,
                coaching.coachee.phone,
                last_note_date,
                last_note_note,
                last_attendance_date,
                section,
                last_tabe,
                last_hiset
            ]
            data.append(s)
        return data

    def get(self, request, *args, **kwargs):
        filename = 'coachee_export.csv'
        coachings = Coaching.objects.filter(
            coach__slug=kwargs['slug'],
            active=True
        ).prefetch_related(
            'coachee__tests'
        ).prefetch_related(
            'coachee__classes__attendance'
        ).prefetch_related(
            'notes'
        )
        data = self.get_student_data(coachings)
        return render_to_csv(data=data, filename=filename)




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
        if 'status' not in context:
            if self.object.notes.count() > 0:
                context['status'] = [
                    ('Concern: Low Grades',
                        self.object.latest_note().low_grades),
                    ('Concern: Class Absences',
                        self.object.latest_note().class_absences),
                    ('Concern: Meeting Absences',
                        self.object.latest_note().meeting_absences),
                    ('Concern: Cannot Reach',
                        self.object.latest_note().cannot_reach),
                    ('Ace Withdrawl',
                        self.object.latest_note().ace_withdrawl)
                ]
            else:
                context['status'] = []
            context.update(kwargs)
        return context


class MeetingNoteCreateView(LoginRequiredMixin, CreateView):

    model = MeetingNote
    form_class = NewMeetingNoteForm
    template_name = 'coaching/meeting_note_form.html'

    def get_context_data(self, **kwargs):
        context = super(MeetingNoteCreateView, self).get_context_data(**kwargs)
        coaching = Coaching.objects.get(pk=self.kwargs['pk'])
        if coaching.notes.count() > 0:
            latest = coaching.latest_note()
        else:
            latest = None
        if 'latest' not in context:
            context['latest'] = latest
            context.update(kwargs)
        return context

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
    form_class = NewMeetingNoteForm
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


class AceRecordUpdateView(LoginRequiredMixin, UpdateView):

    model = AceRecord
    form_class = AceRecordForm
    template_name = 'coaching/ace_record_update.html'

    def get_object(self):
        return AceRecord.objects.get(student__slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(AceRecordUpdateView, self).get_context_data(**kwargs)
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
    form_class = DateFilterForm
    template_name = "coaching/elearn_csv.html"

    def get_student_data(self, students):
        data = []
        headers = [
            "Last Name",
            "First Name",
            "Last Test Date",
            "Coach",
            "Elearn Email",
            "WRU Id",
            "Partner",
        ]

        data.append(headers)

        for student in students:
            try:
                last_test = student.student.tests.last_test
            except ObjectDoesNotExist:
                last_test = 'No test on record'
            try:
                coach = student.student.coaches.filter(active=True).latest('id').coach
            except ObjectDoesNotExist:
                coach = 'No Active Coach'
            s = [
                student.student.last_name,
                student.student.first_name,
                last_test,
                coach,
                student.g_suite_email,
                student.student.partner,
                student.student.WRU_ID,
            ]
            data.append(s)
        return data

    def form_valid(self, form):
        students = ElearnRecord.objects.all()
        filename = "student_list.csv"
        if form.cleaned_data['from_date'] != None:
            from_date = form.cleaned_data['from_date']
            students = students.filter(intake_date__gte=from_date)
        if form.cleaned_data['to_date'] != None:
            to_date = form.cleaned_data['to_date']
            students = students.filter(intake_date__lte=to_date)
        students = students.distinct()
        data = self.get_student_data(students)
        return render_to_csv(data=data, filename=filename)


class ExitExamCSV(LoginRequiredMixin, FormView):

    model = AceRecord
    form_class = DateFilterForm
    template_name = "coaching/exit_exam.html"

    def get_student_data(self, students):
        data = []
        headers = [
            "Last Name",
            "First Name",
            "WRU_ID",
            "ENG 062 Eligible",
            "Read 072 Eligible",
            "MATH 092 Eligible",
            "MATH 098 Eligible",
            "Passed Read 072",
            "Passed ENG 062",
            "Passed Math 092",
            "Passed Math 098",
            "Course History"
        ]

        data.append(headers)

        for student in students:
            enrolled = student.student.active_classes()
            prior = student.student.completed_classes()
            current = []
            completed = []
            towns, eng062, mth092, mth098 = "No", "No", "No", "No"
            for e in enrolled:
                current.append(e.section.title)
            for p in prior:
                completed.append(p.section.title)
            uri = "http://www.dccaep.org" + str(
                    reverse_lazy(
                        'people:student current classes',
                        kwargs={'slug': student.student.slug}
                    )
                )
            s = [
                student.student.last_name,
                student.student.first_name,
                student.student.WRU_ID,
                rules.test_rule('can_eng062', student),
                rules.test_rule('can_read072', student),
                rules.test_rule('can_math092', student),
                rules.test_rule('can_math098', student),
                student.read_072,
                student.eng_062,
                student.math_092,
                student.math_098,
                uri
            ]
            data.append(s)
        return data

    def form_valid(self, form):
        students = AceRecord.objects.all()
        filename = "exit_exam_report.csv"
        data = self.get_student_data(students)
        return render_to_csv(data=data, filename=filename)


class EnrollmentCSV(LoginRequiredMixin, FormView):

    model=None
    form_class = DateFilterForm
    template_name = "coaching/enrollment_csv.html"

    def get_student_data(self, students):
        data = []
        headers = [
            "Last Name",
            "First Name",
            "WRU_ID",
            "Current Classes",
            "Completed Classes"
        ]

        data.append(headers)

        for student in students:
            enrolled = student.student.active_classes()
            prior = student.student.completed_classes()
            current = []
            completed = []
            for e in enrolled:
                current.append(e.section)
            for p in prior:
                completed.append(p.section)
            s = [
                student.student.last_name,
                student.student.first_name,
                student.student.WRU_ID,
                current,
                completed,
            ]
            data.append(s)
        return data

    def form_valid(self, form):
        students = self.model.objects.all()
        filename = "enrollments.csv"
        data = self.get_student_data(students)
        return render_to_csv(data=data, filename=filename)
