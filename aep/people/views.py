from django.views.generic import (
    DetailView, ListView, UpdateView,
    CreateView, TemplateView, FormView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse_lazy, reverse
from assessments.forms import PretestSignupForm, LocatorSignupForm, OrientationSignupForm
from core.utils import render_to_csv
from sections.forms import SectionFilterForm
from .models import Staff, Student, CollegeInterest
from .forms import (
    StaffForm, StudentForm, StudentSearchForm,
    UserForm, UserUpdateForm, WioaForm, CollegeInterestForm)


class UserCreateView(CreateView):
    model = settings.AUTH_USER_MODEL
    form_class = UserForm
    success_url = reverse_lazy('people home')
    template_name = 'people/create_user.html'


# <<<<< Student Views >>>>>

class StudentDetailView(LoginRequiredMixin, DetailView):

    model = Student


class StudentListView(LoginRequiredMixin, ListView, FormView):

    form_class = StudentSearchForm
    queryset = Student.objects.all().order_by('user__last_name', 'user__first_name')
    context_object_name = 'students'
    paginate_by = 25

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


class StudentCSV(LoginRequiredMixin, FormView):

    model = Student
    form_class = SectionFilterForm
    template_name = "people/student_csv.html"

    def get_student_data(self, students):
        data = []
        headers = [
            "WRU Id",
            "Last Name",
            "First Name",
            "Intake Date",
            "DOB",
            "Marital Status",
            "Gender",
            "Address",
            "City",
            "State",
            "Zip",
            "Parish",
            "Email",
            "Phone",
            "Alt Phone",
            "Emergency Contact",
            "Emergency Contact Phone"
        ]
        data.append(headers)
        for student in students:
            s = [
                student.WRU_ID,
                student.user.last_name,
                student.user.first_name,
                str(student.intake_date),
                str(student.dob),
                student.get_marital_status_display(),
                student.get_gender_display(),
                " ".join([
                    student.street_address_1,
                    student.street_address_2
                ]),
                student.city,
                student.state,
                student.zip_code,
                student.get_parish_display(),
                student.user.email,
                student.phone,
                student.alt_phone,
                student.emergency_contact,
                student.ec_phone
            ]
            data.append(s)
        return data


    def form_valid(self, form):
        students = Student.objects.filter(classes__status="A")
        filename = "student_list.csv"
        if form.cleaned_data['site'] != "":
            site = form.cleaned_data['site']
            students = students.filter(classes__section__site=site)
            filename = "_".join([site, filename])
        if form.cleaned_data['program'] != "":
            program = form.cleaned_data['program']
            students = students.filter(classes__section__program=program)
            filename = "_".join([program, filename])

        students = students.distinct()
        data = self.get_student_data(students)
        return render_to_csv(data=data, filename=filename)




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
        user_form = UserUpdateForm(
            request.POST,
            instance=self.get_object().user
        )
        student_form = StudentForm(
            request.POST,
            instance=self.get_object()
        )
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


class NewStudentSignupView(CreateView):

    model = Student
    form_class = StudentForm
    template_name = 'people/sign_up.html'
    success_url = reverse_lazy('people:signup success')

    def get_context_data(self, **kwargs):
        context = super(
            NewStudentSignupView,
            self
        ).get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = UserForm
            context.update(kwargs)
        if 'wioa_form' not in context:
            context['wioa_form'] = WioaForm
            context.update(kwargs)
        if 'orientation_form' not in context:
            context['orientation_form'] = OrientationSignupForm
        return context

    def post(self, request, *args, **kwargs):
        user_form = UserForm(request.POST)
        student_form = StudentForm(request.POST)
        wioa_form = WioaForm(request.POST)
        orientation_form = OrientationSignupForm(request.POST)
        uf_valid = user_form.is_valid()
        sf_valid = student_form.is_valid()
        wf_valid = wioa_form.is_valid()
        of_valid = orientation_form.is_valid()
        if uf_valid and sf_valid and wf_valid and of_valid:
            user = user_form.save()
            student = student_form.save(commit=False)
            student.user = user
            student.save()
            wioa = wioa_form.save(commit=False)
            wioa.student = student
            orientation = orientation_form.save(commit=False)
            orientation. student = student
            wioa.save()
            orientation.save()
            self.object = student
            return HttpResponseRedirect(self.get_success_url())
        else:
            self.object = None
            return self.render_to_response(
                self.get_context_data(
                    user_form=user_form,
                    wioa_form=wioa_form,
                    orientation_form=orientation_form
                )
            )


class StudentCreateSuccessView(TemplateView):

    template_name = 'people/student_create_success.html'


class StudentSignupSuccessView(TemplateView):

    template_name = 'people/signup_success.html'


class CollegeInterestFormView(LoginRequiredMixin, CreateView):

    model = CollegeInterest
    template_name = 'people/college_interest_form.html'
    form_class = CollegeInterestForm

    def get_context_data(self, **kwargs):
        context = super(CollegeInterestFormView, self).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context

    def form_valid(self, form):
        interest = form.save(commit=False)
        student = Student.objects.get(slug=self.kwargs['slug'])
        creator = self.request.user
        interest.student = student
        interest.creator = creator
        interest.save()
        return super(CollegeInterestFormView, self).form_valid(form)


class CollegeInterestDetailView(LoginRequiredMixin, DetailView):

    model = CollegeInterest
    template_name = 'people/college_interest_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CollegeInterestDetailView, self).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context

    def get(self, request, *args, **kwargs):
        try:
            self.object = CollegeInterest.objects.get(student__slug=kwargs['slug'])
        except CollegeInterest.DoesNotExist:
            raise Http404('No College Interest Form has been completed for this student')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


# <<<<< Staff Views >>>>>


class StaffDetailView(LoginRequiredMixin, DetailView):

    model = Staff


class StaffHomeView(LoginRequiredMixin, DetailView):

    model = Staff
    template_name = 'people/staff_home.html'


class StaffListView(LoginRequiredMixin, ListView):

    model = Staff

    queryset = Staff.objects.all().order_by(
        'user__last_name',
        'user__first_name'
    )


class StaffUpdateView(LoginRequiredMixin, UpdateView):

    model = Staff
    template_name = 'people/staff_update.html'
    form_class = StaffForm

    def get_context_data(self, **kwargs):
        context = super(StaffUpdateView, self).get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = UserUpdateForm(instance=self.object.user)
            context.update(kwargs)
        return context

    def post(self, request, *args, **kwargs):
        user_form = UserUpdateForm(
            request.POST,
            instance=self.get_object().user
        )
        staff_form = StaffForm(
            request.POST,
            instance=self.get_object()
        )
        uf_valid = user_form.is_valid()
        sf_valid = staff_form.is_valid()
        if uf_valid and sf_valid:
            user = user_form.save()
            staff = staff_form.save(commit=False)
            staff.user = user
            staff.save()
            self.object = staff
            return HttpResponseRedirect(self.get_success_url())
        else:
            self.object = None
            return self.render_to_response(
                self.get_context_data(user_form=user_form)
            )


class StaffCreateView(LoginRequiredMixin, CreateView):

    model = Staff
    form_class = StaffForm
    template_name = 'people/create_staff.html'

    def get_context_data(self, **kwargs):
        context = super(StaffCreateView, self).get_context_data(**kwargs)
        context['user_form'] = UserForm
        context.update(kwargs)
        return context
