from django.views.generic import DetailView, ListView, UpdateView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from .models import Staff, Student
from .forms import StaffForm, StudentForm, UserForm, UserUpdateForm, WioaForm


class UserCreateView(CreateView):
    model = settings.AUTH_USER_MODEL
    form_class = UserForm
    success_url = reverse_lazy('people home')
    template_name = 'people/create_user.html'


class StudentDetailView(LoginRequiredMixin, DetailView):

    model = Student


class StudentListView(LoginRequiredMixin, ListView):

    model = Student
    context_object_name = 'students'
    paginate_by = 15


class StudentUpdateView(LoginRequiredMixin, UpdateView):

    model = Student
    form_class = StudentForm
    template_name = "people/student_update.html"

    def get_context_data(self, **kwargs):
        context = super(StudentUpdateView, self).get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = UserUpdateForm(instance=self.object.user)
            context.update(kwargs)
        return context

    def post(self, request, *args, **kwargs):
        user_form = UserUpdateForm(request.POST, instance=self.get_object().user)
        student_form = StudentForm(request.POST, instance=self.get_object())
        uf_valid = user_form.is_valid()
        sf_valid = student_form.is_valid()
        if uf_valid and sf_valid:
            user = user_form.save()
            student = student_form.save(commit=False)
            student.user = user
            student.save()
            self.object = student
            return HttpResponseRedirect(self.get_success_url())
        else:
            self.object = None
            return self.render_to_response(
                self.get_context_data(user_form=user_form)
            )


class StudentCreateView(CreateView):

    model = Student
    form_class = StudentForm
    template_name = 'people/create_student.html'
    success_url = reverse_lazy('people:student created')

    def get_context_data(self, **kwargs):
        context = super(StudentCreateView, self).get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = UserForm
            context.update(kwargs)
        if 'wioa_form' not in context:
            context['wioa_form'] = WioaForm
            context.update(kwargs)
        return context

    def post(self, request, *args, **kwargs):
        user_form = UserForm(request.POST)
        student_form = StudentForm(request.POST)
        wioa_form = WioaForm(request.POST)
        uf_valid = user_form.is_valid()
        sf_valid = student_form.is_valid()
        wf_valid = wioa_form.is_valid()
        if uf_valid and sf_valid and wf_valid:
            user = user_form.save()
            student = student_form.save(commit=False)
            student.user = user
            student.save()
            wioa = wioa_form.save(commit=False)
            wioa.student = student
            wioa.save()
            self.object = student
            return HttpResponseRedirect(self.get_success_url())
        else:
            self.object = None
            return self.render_to_response(
                self.get_context_data(user_form=user_form, wioa_form=wioa_form)
            )


class StudentCreateSuccessView(TemplateView):

    template_name = 'people/student_create_success.html'


class StaffDetailView(LoginRequiredMixin, DetailView):

    model = Staff


class StaffHomeView(LoginRequiredMixin, TemplateView):

    model = Staff
    template_name = 'people/staff_home.html'


class StaffListView(LoginRequiredMixin, ListView):

    model = Staff


class StaffUpdateView(LoginRequiredMixin, UpdateView):

    model = Staff


class StaffCreateView(LoginRequiredMixin, CreateView):

    model = Staff
    form_class = StaffForm
    template_name = 'people/create_staff.html'

    def get_context_data(self, **kwargs):
        context = super(StudentCreateView, self).get_context_data(**kwargs)
        context['user_form'] = UserForm
        context.update(kwargs)
        return context
