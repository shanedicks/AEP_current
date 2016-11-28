from django.views.generic import DetailView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from people.models import Student
from .models import Section, Enrollment


class ClassListView(LoginRequiredMixin, ListView):

    model = Section
    template_name = 'sections/class_list.html'


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
    fields = ['student', 'status']

    def form_valid(self, form):
        enrollment = form.save(commit=False)
        section = Section.objects.get(slug=self.kwargs['slug'])
        creator = self.request.user
        enrollment.section = section
        enrollment.creator = creator
        enrollment.save()
        return super(AddStudentView, self).form_valid(form)

    def get_success_url(self):
        url = self.object.section.get_absolute_url()
        return url


class AddClassView(LoginRequiredMixin, CreateView):

    model = Enrollment
    template_name = 'sections/enroll.html'
    fields = ['section']

    def form_valid(self, form):
        enrollment = form.save(commit=False)
        student = Student.objects.get(slug=self.kwargs['slug'])
        creator = self.request.user
        enrollment.student = student
        enrollment.creator = creator
        enrollment.save()
        return super(AddClassView, self).form_valid(form)
