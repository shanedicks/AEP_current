from datetime import timedelta, datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (DetailView, ListView, CreateView,
                                  TemplateView, View, FormView, UpdateView)
from core.utils import render_to_csv
from core.forms import DateFilterForm
from people.models import Student
from .models import (
        TestEvent, TestAppointment, TestHistory,                 
        Tabe, Clas_E, HiSet_Practice, Gain,
    )
from .forms import (
        TestSignupForm, TabeForm, Clas_E_Form,
        GainForm, HiSet_Practice_Form, CSVImportForm,
        TestAppointmentAttendanceForm, TestAttendanceFormSet
    )


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
            "Partner",
            "Student ID",
            "Student Last Name",
            "Student First Name",
            "Test Assignment",
            "Intake Date",
            "Gender",
            "Date of Birth",
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
            try:
                test_assignment = student.student.tests.test_assignment
            except ObjectDoesNotExist:
                test_assignment = 'Missing Test History'
            s = [
                student.student.partner,
                student.student.WRU_ID,
                student.student.last_name,
                student.student.first_name,
                test_assignment,
                student.student.intake_date,
                student.student.get_gender_display(),
                str(student.student.dob),
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


class TestEventAttendanceView(LoginRequiredMixin, UpdateView):

    model = TestEvent
    form_class = TestAppointmentAttendanceForm
    template_name = "assessments/event_attendance.html"

    def get(self, request, *args, **kwargs):
        self.object = TestEvent.objects.get(pk=self.kwargs['pk'])
        attendance_date = self.object.start.date()
        queryset = TestAppointment.objects.filter(
            event=self.object.pk
        ).order_by(
            "student__last_name",
            "student__first_name"
        )
        formset = TestAttendanceFormSet(queryset=queryset)
        return self.render_to_response(
            self.get_context_data(
                formset=formset,
                event=self.object,
                attendance_date=attendance_date
            )
        )

    def post(self, request, *args, **kwargs):
        self.object = TestEvent.objects.get(pk=self.kwargs['pk'])
        formset = TestAttendanceFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(
                self.get_context_data(formset=formset)
            )

    def get_success_url(self):
        return reverse_lazy(
            'assessments:test event detail',
            kwargs={'pk': self.object.pk}
        )


class TabeOnlineCSV(LoginRequiredMixin, View):

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
                student.student.gender,
                student.student.dob.strftime('%m/%d/%Y'),
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
    ).order_by(
        'start',
        'title'
    )

    def get_context_data(self, *args, **kwargs):
        context = super(
            CurrentEventListView,
            self
        ).get_context_data(*args, **kwargs)
        if 'current' not in context:
            context['current'] = True
            context.update(kwargs)
        return context


class PastEventListView(LoginRequiredMixin, ListView):

    model = TestEvent
    template_name = "assessments/test_event_list.html"
    paginate_by = 20
    queryset = TestEvent.objects.filter(
        start__lt=timezone.now()
    ).order_by(
        '-start',
        'title'
    )

    def get_context_data(self, *args, **kwargs):
        context = super(
            PastEventListView,
            self
        ).get_context_data(*args, **kwargs)
        if 'current' not in context:
            context['current'] = False
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
        appt.attendance_date = appt.event.start.date()
        appt.time_in = appt.event.start.time()
        appt.time_out = appt.event.end.time()
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


class TestAppointmentAttendanceView(LoginRequiredMixin, UpdateView):

    model = TestAppointment
    form_class = TestAppointmentAttendanceForm
    template_name = 'assessments/test_appointment_attendance.html'

    def get_success_url(self):
        event = self.object.event
        return reverse_lazy(
            'assessments:test event detail',
            kwargs={'pk': event.pk}
        )


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
        if 'recent_appts' not in context:
            context['recent_appts'] = TestAppointment.objects.filter(
                student__slug=self.kwargs['slug'],
                event__start__lte=timezone.now(),
                event__start__gte=timezone.now() - timedelta(days=30)
            )
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

class TabeCSV(LoginRequiredMixin, FormView):

    model = Tabe
    form_class = DateFilterForm
    template_name = "assessments/tabe_csv.html"

    def get_data(self, tests):
        nrs = {
            '1': 'BEGINNING ABE LITERACY',
            '2': 'BEGINNING BASIC ABE',
            '3': 'LOW INTERMEDIATE ABE',
            '4': 'HIGH INTERMEDIATE ABE',
            '5': 'LOW ASE',
            '6': 'HIGH ASE',
        }
        data = []
        headers = [
            'Partner',
            'SID',
            'LastName',
            'FirstName',
            'AssessmentType',
            'FiscalYear',
            'AssessmentName',
            'AssessmentForm',
            'AssessmentLevel',
            'AssessmentSubject',
            'AssessmentDate',
            'AssessmentScaleScore',
            'AssessmentGradeEquivalent',
            'FunctioningLevel',
            'LowestFunctioningLevelFlag',
            'SurveyIndicator',
            'CompleteBatteryIndicator',
        ]
        data.append(headers)
        for test in tests:
            r = test.read_ss
            m = test.total_math_ss
            l = test.lang_ss
            date = test.test_date
            pre = test.test_date - timedelta(days=180)
            test_type = 'Pretest'
            version = 'TABE'
            if test.form in ('11', '12'):
                version = 'TABE 11 & 12'
            if test.student.tabe_tests.filter(
                test_date__lt=date).filter(
                test_date__gte=pre).count() > 0:
                test_type = 'Posttest'
            if test.read_ss:
                lowest = 1
                if m is not None:
                    if m < r:
                        lowest = 0
                if l is not None:
                    if l < r:
                        lowest = 0
                s = [
                    test.student.student.partner,
                    test.student.student.WRU_ID,
                    test.student.student.last_name,
                    test.student.student.first_name,
                    test_type,
                    '2019-2020',
                    version,
                    test.form,
                    test.read_level,
                    'READING',
                    datetime.strftime(test.test_date, "%m/%d/%Y"),
                    r,
                    test.read_ge,
                    nrs.get(test.read_nrs, ''),
                    lowest,
                    '0',
                    '1',
                ]
                data.append(s)
            if test.total_math_ss:
                lowest = 1
                if r is not None:
                    if r < m:
                        lowest = 0
                if l is not None:
                    if l < m:
                        lowest = 0 
                s = [
                    test.student.student.partner,
                    test.student.student.WRU_ID,
                    test.student.student.last_name,
                    test.student.student.first_name,
                    test_type,
                    '2019-2020',
                    version,
                    test.form,
                    test.math_level,
                    'TOTAL MATH',
                    datetime.strftime(test.test_date, "%m/%d/%Y"),
                    m,
                    test.total_math_ge,
                    nrs.get(test.math_nrs, ''),
                    lowest,
                    '0',
                    '1',
                ]              
                data.append(s)
            if test.lang_ss:
                lowest = 1
                if m is not None:
                    if m < l:
                        lowest = 0
                if r is not None:
                    if r < l:
                        lowest = 0
                s = [
                    test.student.student.partner,
                    test.student.student.WRU_ID,
                    test.student.student.last_name,
                    test.student.student.first_name,
                    test_type,
                    '2019-2020',
                    version,
                    test.form,
                    test.lang_level,
                    'LANGUAGE',
                    datetime.strftime(test.test_date, "%m/%d/%Y"),
                    l,
                    test.lang_ge,
                    nrs.get(test.lang_nrs, ''),
                    lowest,
                    '0',
                    '1',
                ]
                data.append(s)
        return data

    def form_valid(self, form):
        tests = Tabe.objects.select_related().all()
        filename = "tabe_report.csv"
        if form.cleaned_data['from_date'] != "":
            from_date = form.cleaned_data['from_date']
            tests = tests.filter(test_date__gte=from_date)
        if form.cleaned_data['to_date'] != "":
            to_date = form.cleaned_data['to_date']
            tests = tests.filter(test_date__lte=to_date)

        data = self.get_data(tests)
        return render_to_csv(data=data, filename=filename)

class TabeImportCSV(LoginRequiredMixin, FormView):

    model = Tabe
    form_class = CSVImportForm
    template_name = 'assessments/tabe_import.html'

    def form_valid(self, form):
        file = request.Files

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

class ClasECSV(LoginRequiredMixin, FormView):

    model = Clas_E
    form_class = DateFilterForm
    template_name = "assessments/clas-e_csv.html"

    def get_data(self, tests):
        nrs = {
            '1': 'BEGINNING ESL LITERACY',
            '2': 'LOW BEGINNING ESL',
            '3': 'HIGH BEGINNING ESL',
            '4': 'LOW INTERMEDIATE ESL',
            '5': 'HIGH INTERMEDIATE ESL',
            '6': 'ADVANCED ESL',
        }
        data = []
        headers = [
            'Partner',
            'SID',
            'LastName',
            'FirstName',
            'AssessmentType',
            'FiscalYear',
            'AssessmentName',
            'AssessmentForm',
            'AssessmentLevel',
            'AssessmentSubject',
            'AssessmentDate',
            'AssessmentScaleScore',
            'AssessmentGradeEquivalent',
            'FunctioningLevel',
            'LowestFunctioningLevelFlag',
            'SurveyIndicator',
            'CompleteBatteryIndicator',
        ]
        data.append(headers)
        for test in tests:
            date = test.test_date
            pre = test.test_date - timedelta(days=180)
            test_type = 'Pretest'
            if test.student.clas_e_tests.filter(
                test_date__lt=date).filter(
                test_date__gte=pre).count() > 0:
                test_type = 'Posttest'
            s = [
                test.student.student.partner,
                test.student.student.WRU_ID,
                test.student.student.last_name,
                test.student.student.first_name,
                test_type,
                '2018-2019',
                'TABE CLAS-E',
                test.form,
                test.read_level,
                'READING',
                datetime.strftime(test.test_date, "%m/%d/%Y"),
                test.read_ss,
                '',
                nrs.get(test.read_nrs, ''),
                '1',
                '0',
                '1',
            ]
            data.append(s)
        return data

    def form_valid(self, form):
        tests = Clas_E.objects.select_related().all()
        filename = "clas_e_report.csv"
        if form.cleaned_data['from_date'] != "":
            from_date = form.cleaned_data['from_date']
            tests = tests.filter(test_date__gte=from_date)
        if form.cleaned_data['to_date'] != "":
            to_date = form.cleaned_data['to_date']
            tests = tests.filter(test_date__lte=to_date)

        data = self.get_data(tests)
        return render_to_csv(data=data, filename=filename)


class ClasEImportCSV(LoginRequiredMixin, FormView):

    model = Clas_E
    form_class = CSVImportForm
    template_name = 'assessments/clas-e_import.html'

    def form_valid(self, form):
        file = request.Files


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

class GainCSV(LoginRequiredMixin, FormView):

    model = Gain
    form_class = DateFilterForm
    template_name = "assessments/gain_csv.html"

    def get_data(self, tests):
        data = []
        headers = [
            'Partner',
            'SID',
            'LastName',
            'FirstName',
            'AssessmentType',
            'FiscalYear',
            'AssessmentName',
            'AssessmentForm',
            'AssessmentLevel',
            'AssessmentSubject',
            'AssessmentDate',
            'AssessmentScaleScore',
            'AssessmentGradeEquivalent',
            'FunctioningLevel',
            'LowestFunctioningLevelFlag',
            'SurveyIndicator',
            'CompleteBatteryIndicator',
        ]
        data.append(headers)
        for test in tests:
            s = [
                'SID',
                'LastName',
                'FirstName',
                'AssessmentType',
                'FiscalYear',
                'AssessmentName',
                'AssessmentForm',
                'AssessmentLevel',
                'AssessmentSubject',
                'AssessmentDate',
                'AssessmentScaleScore',
                'AssessmentGradeEquivalent',
                'FunctioningLevel',
                'LowestFunctioningLevelFlag',
                'SurveyIndicator',
                'CompleteBatteryIndicator',
            ]
            data.append(s)
        return data

    def form_valid(self, form):
        tests = Gain.objects.select_related().all()
        filename = "Gain_report.csv"
        if form.cleaned_data['from_date'] != "":
            from_date = form.cleaned_data['from_date']
            tests = tests.filter(test_date__gte=from_date)
        if form.cleaned_data['to_date'] != "":
            to_date = form.cleaned_data['to_date']
            tests = tests.filter(test_date__lte=to_date)

        data = self.get_data(tests)
        return render_to_csv(data=data, filename=filename)