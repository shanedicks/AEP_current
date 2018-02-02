
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (DetailView, ListView, CreateView,
                                  TemplateView, View)
from core.utils import render_to_csv
from people.models import Student
from .models import (TestEvent, TestAppointment, TestHistory,
                     Tabe, Clas_E, HiSet_Practice, Gain)
from .forms import (TestSignupForm, TabeForm, Clas_E_Form,
                    GainForm, HiSet_Practice_Form)


class TestingHomeView(LoginRequiredMixin, TemplateView):

    template_name = 'assessments/testing_home.html'


class TestEventDetailView(LoginRequiredMixin, DetailView):

    model = TestEvent
    template_name = 'assessments/test_event_detail.html'
    context_object_name = "event"

    def get_context_data(self, **kwargs):
        context = super(TestEventDetailView, self).get_context_data(**kwargs)
        if 'students' not in context:
            context['students'] = self.object.students.all(
            ).order_by(
                'student__last_name',
                'student__first_name'
            )
            context.update(kwargs)
        return context


class TestEventCSV(LoginRequiredMixin, View):

    def get_student_data(self, students):
        data = []
        headers = [
            "District Code",
            "School Code",
            "Student ID",
            "Student Last Name",
            "Student First Name",
            "Student Middle Initial",
            "Gender",
            "Date of Birth",
            "Intake Date",
            "Marital Status",
            "Address",
            "City",
            "State",
            "Zip",
            "Parish",
            "Email",
            "G-Suite Email",
            "Phone",
            "Alt Phone",
            "Emergency Contact",
            "Emergency Contact Phone"
        ]
        data.append(headers)
        for student in students:
            try:
                g_suite_email = student.student.elearn_record.g_suite_email
            except ObjectDoesNotExist:
                g_suite_email = ""
            s = [
                "1142370",
                "1153531",
                student.student.WRU_ID,
                student.student.last_name,
                student.student.first_name,
                "",
                student.student.get_gender_display(),
                str(student.student.dob),
                student.student.intake_date,
                student.student.get_marital_status_display(),
                " ".join([
                    student.student.street_address_1,
                    student.student.street_address_2
                ]),
                student.student.city,
                student.student.state,
                student.student.zip_code,
                student.student.get_parish_display(),
                student.student.email,
                g_suite_email,
                student.student.phone,
                student.student.alt_phone,
                student.student.emergency_contact,
                student.student.ec_phone
            ]
            data.append(s)
        return data

    def get(self, request, *args, **kwargs):
        event = TestEvent.objects.get(
            pk=self.kwargs['pk'])
        filename = "student_list.csv"
        students = event.students.prefetch_related(
            'student', 'student__user'
        )
        data = self.get_student_data(students)
        return render_to_csv(data=data, filename=filename)


class TestEventListView(LoginRequiredMixin, ListView):

    model = TestEvent
    template_name = "assessments/test_event_list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(
            TestEventListView,
            self
        ).get_context_data(*args, **kwargs)
        if 'upcoming' not in context:
            context['upcoming'] = TestEvent.objects.filter(
                start__gte=timezone.now()
            )
            context.update(kwargs)
        if 'past' not in context:
            context['past'] = TestEvent.objects.filter(
                start__lt=timezone.now()
            )
            context.update(kwargs)
        return context


class CurrentEventListView(LoginRequiredMixin, ListView):

    model = TestEvent
    template_name = "assessments/test_event_list.html"
    queryset = TestEvent.objects.filter(
        start__gte=timezone.now()
    )

    def get_context_data(self, *args, **kwargs):
        context = super(
            CurrentEventListView,
            self
        ).get_context_data(*args, **kwargs)
        if 'tempus' not in context:
            context['tempus'] = "Current"
            context.update(kwargs)
        return context


class PastEventListView(LoginRequiredMixin, ListView):

    model = TestEvent
    template_name = "assessments/test_event_list.html"
    paginate_by = 20
    queryset = TestEvent.objects.filter(
        start__lt=timezone.now()
    )

    def get_context_data(self, *args, **kwargs):
        context = super(
            PastEventListView,
            self
        ).get_context_data(*args, **kwargs)
        if 'tempus' not in context:
            context['tempus'] = "Past"
            context.update(kwargs)
        return context



class TestingSignupView(LoginRequiredMixin, CreateView):

    model = TestAppointment
    form_class = TestSignupForm
    template_name = 'assessments/test_signup.html'

    def get_context_data(self, **kwargs):
        context = super(
            TestingSignupView,
            self
        ).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context

    def form_valid(self, form):
        student = Student.objects.get(slug=self.kwargs['slug'])
        appt = form.save(commit=False)
        appt.student = student
        try:
            appt.save()
            return super(TestingSignupView, self).form_valid(form)
        except IntegrityError:
            form.add_error(
                'event',
                'This student is already signed up for the selected Test Event'
            )
            return self.form_invalid(form)


class TestAppointmentDetailView(LoginRequiredMixin, DetailView):

    model = TestAppointment
    template_name = 'assessments/test_appointment_detail.html'
    context_object_name = "appt"


class StudentTestHistoryView(LoginRequiredMixin, DetailView):

    model = TestHistory
    template_name = 'assessments/student_test_history.html'
    context_object_name = 'history'

    def get(self, request, *args, **kwargs):
        try:
            self.object = TestHistory.objects.get(student__slug=kwargs['slug'])
        except TestHistory.DoesNotExist:
            return HttpResponseRedirect(reverse('assessments:no history'))
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(
            StudentTestHistoryView,
            self
        ).get_context_data(**kwargs)
        if 'appts' not in context:
            context['appts'] = TestAppointment.objects.filter(
                student__slug=self.kwargs['slug'],
                event__start__gte=timezone.now()
            ).order_by('event__start')
            context.update(kwargs)
        return context


class NoHistoryView(TemplateView):

    template_name = 'assessments/no_history.html'


class StudentTestListView(LoginRequiredMixin, ListView):

    class Meta:
        abstract = True

    def get_context_data(self, **kwargs):
        context = super(
            StudentTestListView,
            self
        ).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context

    def get_queryset(self, **kwargs):
        qst = self.model.objects.filter(
            student__student__slug=self.kwargs['slug']
        ).order_by('-test_date')
        return qst


class StudentTestDetailView(LoginRequiredMixin, DetailView):

    class Meta:
        abstract = True

    def get_context_data(self, **kwargs):
        context = super(
            StudentTestDetailView,
            self
        ).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context


class StudentTestAddView(LoginRequiredMixin, CreateView):

    class Meta:
        abstract = True

    def get_context_data(self, **kwargs):
        context = super(
            StudentTestAddView,
            self
        ).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context

    def form_valid(self, form):
        test = form.save(commit=False)
        student = TestHistory.objects.get(student__slug=self.kwargs['slug'])
        test.student = student
        return super(StudentTestAddView, self).form_valid(form)


class StudentTabeListView(StudentTestListView):

    model = Tabe
    template_name = 'assessments/student_tabe_list.html'


class StudentTabeAddView(StudentTestAddView):

    model = Tabe
    form_class = TabeForm
    template_name = 'assessments/student_tabe_add.html'

    def get_success_url(self):
        return reverse(
            "assessments:student test history",
            kwargs={'slug': self.kwargs['slug']}
        )


class StudentTabeDetailView(StudentTestDetailView):

    model = Tabe
    template_name = 'assessments/student_tabe_detail.html'


class StudentClasEListView(StudentTestListView):

    model = Clas_E
    template_name = 'assessments/student_clas-e_list.html'


class StudentClasEAddView(StudentTestAddView):

    model = Clas_E
    form_class = Clas_E_Form
    template_name = 'assessments/student_clas-e_add.html'

    def get_success_url(self):
        return reverse(
            "assessments:student test history",
            kwargs={'slug': self.kwargs['slug']}
        )


class StudentClasEDetailView(StudentTestDetailView):

    model = Clas_E
    template_name = 'assessments/student_clas-e_detail.html'


class StudentHisetPracticeListView(StudentTestListView):

    model = HiSet_Practice
    template_name = 'assessments/student_hiset_practice_list.html'


class StudentHisetPracticeAddView(StudentTestAddView):

    model = HiSet_Practice
    form_class = HiSet_Practice_Form
    template_name = 'assessments/student_hiset_practice_add.html'

    def form_valid(self, form):
        test = form.save(commit=False)
        submitter = self.request.user
        test.reported_by = submitter
        return super(StudentHisetPracticeAddView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            "assessments:student test history",
            kwargs={'slug': self.kwargs['slug']}
        )


class StudentHisetPracticeDetailView(StudentTestDetailView):

    model = HiSet_Practice
    template_name = 'assessments/student_hiset_practice_detail.html'


class StudentGainListView(StudentTestListView):

    model = Gain
    template_name = 'assessments/student_gain_list.html'


class StudentGainAddView(StudentTestAddView):

    model = Gain
    form_class = GainForm
    template_name = 'assessments/student_gain_add.html'

    def get_success_url(self):
        return reverse(
            "assessments:student test history",
            kwargs={'slug': self.kwargs['slug']}
        )


class StudentGainDetailView(StudentTestDetailView):

    model = Gain
    template_name = 'assessments/student_gain_detail.html'
