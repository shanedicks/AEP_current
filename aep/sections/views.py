from datetime import datetime
from django.views.generic import (DetailView, ListView, CreateView,
                                  DeleteView, UpdateView, FormView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.db import IntegrityError
from core.utils import render_to_csv
from people.models import Student
from people.forms import StudentSearchForm
from .models import Section, Enrollment, Attendance
from .forms import (SectionFilterForm, ClassAddEnrollmentForm,
                    ClassAddFromListEnrollForm, StudentAddEnrollmentForm,
                    SingleAttendanceForm, AttendanceFormSet, SectionSearchForm,
                    AdminAttendanceForm, AttReportFilterForm)


class AttendanceCSV(LoginRequiredMixin, FormView):

    model = Attendance
    form_class = AttReportFilterForm
    template_name = "sections/attendance_report_csv.html"

    def get_data(self, attendance):
        data = []
        headers = [
            'attendance_type',
            'attendance_date',
            'time_in',
            'time_out',
            'student__WRU_ID',
            'last_name',
            'first_name',
            'WRU_ID'
        ]
        data.append(headers)
        for att in attendance:
            s = [
                att.attendance_type,
                att.attendance_date,
                att.time_in,
                att.time_out,
                att.enrollment.student.WRU_ID,
                att.enrollment.student.user.last_name,
                att.enrollment.student.user.first_name,
                att.enrollment.section.WRU_ID
            ]
            data.append(s)
        return data

    def form_valid(self, form):
        attendance = Attendance.objects.select_related().all()
        filename = "attendance_report.csv"
        if form.cleaned_data['from_date'] != "":
            from_date = form.cleaned_data['from_date']
            attendance = attendance.filter(attendance_date__gte=from_date)
        if form.cleaned_data['to_date'] != "":
            to_date = form.cleaned_data['to_date']
            attendance = attendance.filter(attendance_date__lte=to_date)

        data = self.get_data(attendance)
        return render_to_csv(data=data, filename=filename)


class ClassListView(LoginRequiredMixin, ListView, FormView):

    form_class = SectionSearchForm
    model = Section
    template_name = 'sections/class_list.html'
    paginate_by = 20

    queryset = Section.objects.filter(
        semester__end_date__gte=datetime.today().date()
    ).order_by('site', 'program', 'title')

    def get_form_kwargs(self):
        return {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
            'data': self.request.GET or None
        }

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        form = self.get_form(self.get_form_class())
        if form.is_valid():
            self.object_list = form.filter_queryset(request, self.object_list)
        return self.render_to_response(
            self.get_context_data(form=form, object_list=self.object_list)
        )


class AddClassListView(ClassListView):

    template_name = 'sections/add_class_list.html'


class ClassDetailView(LoginRequiredMixin, DetailView):

    model = Section
    template_name = 'sections/class_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ClassDetailView, self).get_context_data(**kwargs)
        if 'students' not in context:
            context['students'] = self.object.get_all_students(
            ).order_by(
                'student__user__last_name',
                'student__user__first_name'
            )
        return context


class ClassTestingPreview(ClassDetailView):

    template_name = 'sections/class_testing_preview.html'

    def get_context_data(self, **kwargs):
        context = super(ClassTestingPreview, self).get_context_data(**kwargs)
        context['students'] = self.object.get_active(
        ).order_by(
            'student__user__last_name',
            'student__user__first_name'
        )
        return context

class PrintSignInView(LoginRequiredMixin, DetailView):

    model = Section
    template_name = 'sections/print_sign-in.html'

    def get_context_data(self, **kwargs):
        context = super(PrintSignInView, self).get_context_data(**kwargs)
        if 'attendance_date' not in context:
            context['attendance_date'] = self.kwargs['attendance_date']
        if 'active' not in context:
            context['active'] = self.object.get_active(
            ).order_by(
                'student__user__last_name',
                'student__user__first_name'
            )
        return context


class StudentClassListView(LoginRequiredMixin, ListView):

    model = Enrollment
    template_name = 'sections/student_class_list.html'

    def get_context_data(self, **kwargs):
        context = super(StudentClassListView, self).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        if 'today' not in context:
            context['today'] = datetime.today().date()
            context.update(kwargs)
        return context

    def get_queryset(self):
        if 'slug' in self.kwargs:
            slug = self.kwargs['slug']
            return Enrollment.objects.filter(
                student__slug=slug
            ).order_by(
                "section__semester__start_date",
                "section__tuesday",
                "section__start_time"
            ).prefetch_related('attendance')


class StudentScheduleView(StudentClassListView):

    template_name = 'sections/student_schedule.html'


class StudentAttendanceView(StudentClassListView):

    template_name = 'sections/student_attendance.html'


class AddStudentView(LoginRequiredMixin, CreateView):

    model = Enrollment
    template_name = 'sections/enroll_student.html'
    form_class = StudentAddEnrollmentForm

    def form_valid(self, form):
        enrollment = form.save(commit=False)
        section = Section.objects.get(slug=self.kwargs['slug'])
        creator = self.request.user
        enrollment.section = section
        enrollment.creator = creator
        try:
            enrollment.save()
            return super(AddStudentView, self).form_valid(form)
        except IntegrityError:
            form.add_error(
                'student',
                'The selected student is already enrolled in this class'
            )
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(AddStudentView, self).get_form_kwargs()
        if self.request.GET:
            kwargs.update(self.request.GET)
        return kwargs

    def get_success_url(self):
        url = self.object.section.get_absolute_url()
        return url


class AddClassView(LoginRequiredMixin, CreateView):

    model = Enrollment
    template_name = 'sections/enroll.html'
    form_class = ClassAddEnrollmentForm

    def get_context_data(self, **kwargs):
        context = super(AddClassView, self).get_context_data(**kwargs)
        if 'filter_form' not in context:
            context['filter_form'] = SectionFilterForm()
            context.update(kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context

    def get_form_kwargs(self):
        kwargs = super(AddClassView, self).get_form_kwargs()
        if self.request.GET:
            kwargs.update(self.request.GET)
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        filter_form = SectionFilterForm(request.GET, None)
        return self.render_to_response(
            self.get_context_data(
                filter_form=filter_form,
                form=form
            )
        )

    def form_valid(self, form):
        enrollment = form.save(commit=False)
        student = Student.objects.get(slug=self.kwargs['slug'])
        creator = self.request.user
        enrollment.student = student
        enrollment.creator = creator
        if student.tests.last_test is None and enrollment.section.program != 'TRANS':
            form.add_error(
                None,
                'This student has no pre-test on record,'
                ' and cannot be enrolled at this time.'
                ' Please talk to a Site Team Leader about next steps.'
            )
            return self.form_invalid(form)
        try:
            enrollment.save()
            return super(AddClassView, self).form_valid(form)
        except IntegrityError:
            form.add_error(
                'section',
                'This student is already enrolled in the selected class'
            )
            return self.form_invalid(form)

    def get_success_url(self):
        student = Student.objects.get(slug=self.kwargs['slug'])
        url = student.get_absolute_url()
        return url + "my-classes"


class AddClassFromListView(LoginRequiredMixin, CreateView):

    model = Enrollment
    template_name = 'sections/check_enroll.html'
    form_class = ClassAddFromListEnrollForm

    def get_context_data(self, **kwargs):
        context = super(AddClassFromListView, self).get_context_data(**kwargs)
        if 'section' not in context:
            context['section'] = Section.objects.get(pk=self.kwargs['pk'])
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
        context.update(kwargs)
        return context

    def form_valid(self, form):
        enrollment = form.save(commit=False)
        section = Section.objects.get(pk=self.kwargs['pk'])
        student = Student.objects.get(slug=self.kwargs['slug'])
        creator = self.request.user
        enrollment.section = section
        enrollment.student = student
        enrollment.creator = creator
        try:
            enrollment.save()
            return super(AddClassFromListView, self).form_valid(form)
        except IntegrityError:
            form.add_error(
                'section',
                'This student is already enrolled in the selected class'
            )
            return self.form_invalid(form)

    def get_success_url(self):
        student = Student.objects.get(slug=self.kwargs['slug'])
        url = student.get_absolute_url()
        return url + "my-classes"


class EnrollmentView(LoginRequiredMixin, DetailView):

    model = Enrollment


class EnrollmentDeleteView(LoginRequiredMixin, DeleteView):

    model = Enrollment

    def get_success_url(self):
        student = self.object.student
        return reverse_lazy(
            'people:student classes',
            kwargs={'slug': student.slug}
        )


class AttendanceOverview(LoginRequiredMixin, DetailView):

    model = Section
    template_name = 'sections/attendance_overview.html'

    def get_context_data(self, **kwargs):
        context = super(AttendanceOverview, self).get_context_data()
        if 'days' not in context:
            context['days'] = self.object.get_class_dates()
        if 'active' not in context:
            context['active'] = self.object.get_active(
            ).order_by(
                'student__user__last_name',
                'student__user__first_name'
            ).prefetch_related('attendance')
        if 'dropped' not in context:
            context['dropped'] = self.object.get_dropped(
            ).order_by(
                'student__user__last_name',
                'student__user__first_name'
            ).prefetch_related('attendance')
        if 'waitlist' not in context:
            context['waitlist'] = self.object.get_waiting(
            ).order_by(
                'student__user__last_name',
                'student__user__first_name'
            ).prefetch_related('attendance')
        return context


class SingleAttendanceView(LoginRequiredMixin, UpdateView):

    model = Attendance
    form_class = SingleAttendanceForm

    def get_success_url(self):
        section = self.object.enrollment.section
        return reverse_lazy(
            'sections:attendance overview',
            kwargs={'slug': section.slug}
        )


class AdminAttendanceView(LoginRequiredMixin, CreateView):

    model = Attendance
    template_name = 'sections/attendance_form.html'
    form_class = AdminAttendanceForm

    def form_valid(self, form):
        att = form.save(commit=False)
        enrollment = Enrollment.objects.get(pk=self.kwargs['pk'])
        att.attendance_type = 'P'
        att.enrollment = enrollment
        att.save()
        return super(AdminAttendanceView, self).form_valid(form)

    def get_success_url(self):
        section = Enrollment.objects.get(pk=self.kwargs['pk']).section
        return reverse_lazy(
            'sections:attendance overview',
            kwargs={'slug': section.slug}
        )


class DailyAttendanceView(LoginRequiredMixin, UpdateView):

    model = Section
    form_class = SingleAttendanceForm
    template_name = 'sections/daily_attendance.html'

    def get(self, request, *args, **kwargs):
        self.object = Section.objects.get(slug=self.kwargs['slug'])
        attendance_date = self.kwargs['attendance_date']
        queryset = Attendance.objects.filter(
            enrollment__section=self.object,
            enrollment__status="A",
            attendance_date=attendance_date
        ).order_by(
            "enrollment__student__user__last_name",
            "enrollment__student__user__first_name"
        )
        formset = AttendanceFormSet(queryset=queryset)
        return self.render_to_response(
            self.get_context_data(
                formset=formset,
                section=self.object,
                attendance_date=attendance_date
            )
        )

    def post(self, request, *args, **kwargs):
        self.object = Section.objects.get(slug=self.kwargs['slug'])
        formset = AttendanceFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(
                self.get_context_data(formset=formset)
            )

    def get_success_url(self):
        section = self.object
        return reverse_lazy(
            'sections:attendance overview',
            kwargs={'slug': section.slug}
        )
