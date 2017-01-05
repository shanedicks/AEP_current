from django.views.generic import (DetailView, ListView, CreateView,
                                  DeleteView, UpdateView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.db import IntegrityError
from people.models import Student
from people.forms import StudentSearchForm
from .models import Section, Enrollment, Attendance
from .forms import (SectionFilterForm, ClassAddEnrollmentForm,
                    ClassAddFromListEnrollForm, StudentAddEnrollmentForm,
                    SingleAttendanceForm, AttendanceFormSet)


class ClassListView(LoginRequiredMixin, ListView):

    model = Section
    template_name = 'sections/class_list.html'
    paginate_by = 20

    queryset = Section.objects.all().order_by('site', 'program', 'title')


class AddClassListView(ClassListView):

    template_name = 'sections/add_class_list.html'


class ClassDetailView(LoginRequiredMixin, DetailView):

    model = Section
    template_name = 'sections/class_detail.html'


class StudentClassListView(LoginRequiredMixin, ListView):

    model = Enrollment
    template_name = 'sections/student_class_list.html'

    def get_context_data(self, **kwargs):
        context = super(StudentClassListView, self).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context

    def get_queryset(self):
        if 'slug' in self.kwargs:
            slug = self.kwargs['slug']
            return Enrollment.objects.filter(student__slug=slug).order_by("section__tuesday", "section__start_time")


class StudentScheduleView(StudentClassListView):

    template_name = 'sections/student_schedule.html'


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
            "enrollment__student"
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



