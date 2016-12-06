from django.views.generic import DetailView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import IntegrityError
from people.models import Student
from .models import Section, Enrollment
from .forms import SectionFilterForm, ClassAddEnrollementForm


class ClassListView(LoginRequiredMixin, ListView):

    model = Section
    template_name = 'sections/class_list.html'


class AddClassListView(ClassListView):

    template_name = 'sections/add_class_list.html'


class ClassDetailView(LoginRequiredMixin, DetailView):

    model = Section
    template_name = 'sections/class_detail.html'


class StudentClassListView(LoginRequiredMixin, ListView):

    model = Enrollment
    template_name = 'sections/student_class_list.html'

    def get_queryset(self):
        if 'slug' in self.kwargs:
            slug = self.kwargs['slug']
            return Enrollment.objects.filter(student__slug=slug)


class AddStudentView(LoginRequiredMixin, CreateView):

    model = Enrollment
    template_name = 'sections/enroll_student.html'
    fields = ['student']

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

    def get_success_url(self):
        url = self.object.section.get_absolute_url()
        return url


class AddClassView(LoginRequiredMixin, CreateView):

    model = Enrollment
    template_name = 'sections/enroll.html'
    form_class = ClassAddEnrollementForm

    def get_context_data(self, **kwargs):
        context = super(AddClassView, self).get_context_data(**kwargs)
        if 'filter_form' not in context:
            context['filter_form'] = SectionFilterForm()
            context.update(kwargs)
        return context
    '''
    def get_form_kwargs(self):
        kwargs = super(AddClassView, self).get_form_kwargs()
        kwargs.update(self.request.GET)
        return kwargs
    '''

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        qst = Section.objects.all()
        if 'site' in request.GET:
            site, program = request.GET['site'], request.GET['program']
            if site != '':
                qst = qst.filter(site=site)
            if program != '':
                qst = qst.filter(program=program)
        form_class.base_fields['section'].queryset = qst
        form = self.get_form(form_class)
        filter_form = SectionFilterForm(request.GET, None)
        return self.render_to_response(
            self.get_context_data(
                form=form,
                filter_form=filter_form
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
