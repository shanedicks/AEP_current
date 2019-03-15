from django.views.generic import (
    DetailView, ListView, UpdateView,
    CreateView, TemplateView, FormView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import HttpResponseRedirect, Http404
from django.template.loader import get_template
from django.template import Context
from django.urls import reverse_lazy, reverse
from formtools.wizard.views import SessionWizardView
from assessments.forms import OrientationSignupForm
from core.forms import DateFilterForm
from core.utils import render_to_csv
from core.tasks import send_mail_task, email_multi_alternatives_task
from sections.forms import SectionFilterForm
from .models import Staff, Student, CollegeInterest, WIOA
from .forms import (
    StaffForm, StudentPersonalInfoForm, StudentSearchForm,
    StudentInterestForm, StudentContactForm, SSNForm, REForm,
    EETForm, AdditionalDetailsForm, DisabilityForm, StudentForm,
    UserForm, UserUpdateForm, WioaForm, CollegeInterestForm, PartnerForm,
    StudentComplianceForm
    )


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
    queryset = Student.objects.filter(duplicate=False).order_by('last_name', 'first_name')
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


class ActiveStudentCSV(LoginRequiredMixin, FormView):

    model = Student
    form_class = SectionFilterForm
    template_name = "people/active_student_csv.html"

    def get_student_data(self, students):
        data = []
        headers = [
            "WRU Id",
            "Last Name",
            "First Name",
            "Intake Date",
            'Partner',
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
                student.last_name,
                student.first_name,
                str(student.intake_date),
                student.partner,
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
                student.email,
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


class NewStudentCSV(ActiveStudentCSV):

    form_class = DateFilterForm
    template_name = "people/new_student_csv.html"

    def form_valid(self, form):
        students = Student.objects.filter(duplicate=False)
        filename = "student_list.csv"
        if form.cleaned_data['from_date'] != "":
            from_date = form.cleaned_data['from_date']
            students = students.filter(intake_date__gte=from_date)
        if form.cleaned_data['to_date'] != "":
            to_date = form.cleaned_data['to_date']
            students = students.filter(intake_date__lte=to_date)

        students = students.distinct()
        data = self.get_student_data(students)
        return render_to_csv(data=data, filename=filename)


class StudentUpdateView(LoginRequiredMixin, UpdateView):

    model = Student
    form_class = StudentForm
    template_name = "people/student_update.html"


class StudentComplianceFormView(LoginRequiredMixin, UpdateView):

    model = Student
    form_class = StudentComplianceForm
    template_name = "people/student_compliance.html"


class StudentCreateView(CreateView):

    model = Student
    form_class = StudentForm
    template_name = 'people/create_student.html'
    success_url = reverse_lazy('people:student created')

    def get_context_data(self, **kwargs):
        context = super(StudentCreateView, self).get_context_data(**kwargs)
        if 'wioa_form' not in context:
            context['wioa_form'] = WioaForm
            context.update(kwargs)
        return context

    def post(self, request, *args, **kwargs):
        student_form = StudentForm(request.POST)
        wioa_form = WioaForm(request.POST)
        sf_valid = student_form.is_valid()
        wf_valid = wioa_form.is_valid()
        if sf_valid and wf_valid:
            student = student_form.save(commit=False)
            student.save()
            wioa = wioa_form.save(commit=False)
            wioa.student = student
            wioa.save()
            self.object = student
            return HttpResponseRedirect(self.get_success_url())
        else:
            self.object = None
            return self.render_to_response(
                self.get_context_data(wioa_form=wioa_form)
            )


class PartnerStudentCreateView(LoginRequiredMixin, CreateView):

    model = Student
    form_class = PartnerForm
    template_name = 'people/partner_student.html'
    success_url = reverse_lazy('people:student created')


class StudentSignupWizard(SessionWizardView):

    form_list = [
        ("personal", StudentPersonalInfoForm),
        ("ssn", SSNForm),
        ("interest", StudentInterestForm),
        ("contact", StudentContactForm),
        ("race", REForm),
        ("EET", EETForm),
        ("disability", DisabilityForm),
        ("details", AdditionalDetailsForm),
        ("signup", OrientationSignupForm)
    ]

    template_name = "people/sign_up_wizard.html"

    def done(self, form_list, form_dict, **kwargs):
        ssn = self.get_cleaned_data_for_step('ssn')
        personal = self.get_cleaned_data_for_step('personal')
        interest = self.get_cleaned_data_for_step('interest')
        contact = self.get_cleaned_data_for_step('contact')
        race = self.get_cleaned_data_for_step('race')
        eet = self.get_cleaned_data_for_step('EET')
        disability = self.get_cleaned_data_for_step('disability')
        details = self.get_cleaned_data_for_step('details')
        student = Student(**personal, **interest, **contact)
        student.save()
        wioa = WIOA(**ssn, **race, **eet, **disability, **details)
        wioa.student = student
        wioa.save()
        orientation = form_dict["signup"].save(commit=False)
        orientation.student = student
        orientation.save()
        if student.email:
            send_mail_task.delay(
                subject="Thank you for registering for the Delgado "
                "Community College Adult Education Program!",
                message="",
                html_message="<p>Hi, {student}</p><p>You have selected "
                "to attend Orientation on {date:{dfmt}} at {time:{tfmt}} "
                "at the City Park Campus (615 City Park Ave,"
                " New Orleans, LA 70119), though you can "
                "later choose to attend classes at other locations. "
                "For orientation and testing, please come to Building "
                "7, Room 170. Click <a href='http://www.dcc.edu/about/"
                "locations/city-park/cp-directions.aspx'>here</a>"
                " for directions and click <a href='http://www.dcc."
                "edu/documents/about/cp-campus-map.pdf'>here</a>"
                " for a map of the campus.</p>"
                "<br>"
                "<p><strong>Your attendance of this event is required"
                " to move forward in the registration process</strong>"
                ". Please call 504-671-5434 or email adulted@dcc.edu "
                "if you have any questions or need to reschedule.</p>"
                "<br><p>Thank you,</p>"
                "<p>The Adult Education Program</p>"
                "<p>Delgado Community College</p>".format(
                    student=student.first_name,
                    dfmt="%A, %B %d",
                    tfmt="%I:%M %p",
                    date=orientation.event.start.date(),
                    time=orientation.event.start.time()
                ),
                from_email="reminder@dccaep.org",
                recipient_list=[student.email],
            )
        return HttpResponseRedirect(reverse_lazy('people:signup success'))


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
            orientation.student = student
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


class ElearnSignupSuccessView(TemplateView):

    template_name = 'people/elearn_success.html'


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

    def get_context_data(self, **kwargs):
        context = super(StaffHomeView, self).get_context_data(**kwargs)
        if 'coachees' not in context:
            context['coachees'] = self.object.coachees.filter(active=True)
            context.update(kwargs)
        return context


class StaffListView(LoginRequiredMixin, ListView):

    model = Staff

    def get_context_data(self, **kwargs):
        context = super(StaffListView, self).get_context_data(**kwargs)
        if 'full_time' not in context:
            context['full_time'] = Staff.objects.filter(
                full_time=True,
                active=True
            ).order_by(
                'last_name',
                'first_name'
            )
            context.update(kwargs)
        if 'part_time' not in context:
            context['part_time'] = Staff.objects.filter(
                full_time=False,
                active=True
            ).order_by(
                'last_name',
                'first_name'
            )
        return context


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
