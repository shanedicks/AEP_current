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
        Tabe, Clas_E, HiSet_Practice, Gain, HiSET, Accuplacer
    )
from .forms import (
        TestSignupForm, TabeForm, Clas_E_Form,
        GainForm, HiSet_Practice_Form, CSVImportForm,
        TestAppointmentAttendanceForm, TestAttendanceFormSet,
        TestAppointmentNotesForm, HiSetForm, AccuplacerForm,
        Clas_E_ScoreReportLinkForm, TabeScoreReportLinkForm
    )
from .tasks import (event_attendance_report_task,
        accelerated_coaching_report_task, testing_eligibility_report,
        send_score_report_link_task
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
            context['students'] = self.object.students.filter(
                student__duplicate=False
            ).order_by(
                'student__last_name',
                'student__first_name'
            )
            context.update(kwargs)
        return context


class TestEventAttendanceReport(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        event = TestEvent.objects.get(
            pk=self.kwargs['pk'])
        user_email = request.user.email
        event_attendance_report_task.delay(event.id, user_email)
        return HttpResponseRedirect(reverse('assessments:test event detail', args=(event.pk,)))


class TestingEligibilityReportView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        user_email = request.user.email
        testing_eligibility_report.delay(user_email)
        return HttpResponseRedirect(reverse_lazy('report success'))


class AcceleratedCoachingReport(LoginRequiredMixin, FormView):

    form_class = DateFilterForm
    template_name = "assessments/accelerated_coaching_report.html"
    success_url = reverse_lazy('report success')

    def form_valid(self, form):
        from_date = form.cleaned_data['from_date']
        to_date = form.cleaned_data['to_date']
        email = self.request.user.email
        accelerated_coaching_report_task.delay(from_date, to_date, email)
        return super().form_valid(form)


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
            "CCR",
            "ELL",
            "ACE",
            "eLearn",
            "Success",
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
                student.student.ccr_app,
                student.student.ell_app,
                student.student.ace_app,
                student.student.e_learn_app,
                student.student.success_app,
                student.student.gender,
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
        queryset = TestAppointment.objects.filter(
            student__duplicate=False,
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
            )
        )

    def post(self, request, *args, **kwargs):
        self.object = TestEvent.objects.get(pk=self.kwargs['pk'])
        queryset = TestAppointment.objects.filter(
            student__duplicate=False,
            event=self.object.pk
        ).order_by(
            "student__last_name",
            "student__first_name"
        )
        formset = TestAttendanceFormSet(request.POST, queryset=queryset)
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
                "LA23680",
                "LA20001",
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


class TestAppointmentNotesView(LoginRequiredMixin, UpdateView):

    model = TestAppointment
    form_class = TestAppointmentNotesForm
    template_name = 'assessments/test_appointment_notes.html'


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

class TestAppointmentListView(LoginRequiredMixin, ListView):

    model = TestAppointment
    template_name = 'assessments/student_test_appointments.html'
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(TestAppointmentListView, self).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context

    def get_queryset(self, **kwargs):
        qst = TestAppointment.objects.filter(
            student__slug=self.kwargs['slug']
        ).order_by('-event__start')
        return qst


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

    def get_success_url(self):
        return reverse(
            "assessments:student test history",
            kwargs={'slug': self.kwargs['slug']}
        )


class StudentTabeListView(StudentTestListView):

    model = Tabe
    template_name = 'assessments/student_tabe_list.html'


class StudentTabeAddView(StudentTestAddView):

    model = Tabe
    form_class = TabeForm
    template_name = 'assessments/student_tabe_add.html'

class StudentTabeDetailView(StudentTestDetailView):

    model = Tabe
    template_name = 'assessments/student_tabe_detail.html'


class TabeScoreReportLinkFormView(LoginRequiredMixin, UpdateView):

    model = Tabe
    form_class = TabeScoreReportLinkForm
    template_name = 'assessments/score_report_link.html'

    def get_success_url(self):
        return reverse(
            "assessments:student tabe list",
            kwargs={'slug': self.kwargs['slug']}
        )


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
                if test.student.tabe_tests.filter(
                    test_date__lt=date).filter(
                    test_date__gte=pre,
                    read_ss__isnull=False).count() > 0:
                    test_type = 'Posttest'
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
                    '2022-2023',
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
                if test.student.tabe_tests.filter(
                    test_date__lt=date).filter(
                    test_date__gte=pre,
                    total_math_ss__isnull=False).count() > 0:
                    test_type = 'Posttest'
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
                    '2022-2023',
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
                if test.student.tabe_tests.filter(
                    test_date__lt=date).filter(
                    test_date__gte=pre,
                    lang_ss__isnull=False).count() > 0:
                    test_type = 'Posttest'
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
                    '2022-2023',
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


class ClasEScoreReportLinkFormView(LoginRequiredMixin, UpdateView):

    model = Clas_E
    form_class = Clas_E_ScoreReportLinkForm
    template_name = 'assessments/score_report_link.html'

    def get_success_url(self):
        return reverse(
            "assessments:student clas-e list",
            kwargs={'slug': self.kwargs['slug']}
        )


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
                '2022-2023',
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


class TestScoreStorageCSV(LoginRequiredMixin, FormView):

    form_class = DateFilterForm
    template_name = 'assessments/test_score_storage.html'

    def get_data(self, clas_es, tabes):
        data = []
        headers = [
            'Test',
            'WRU_ID',
            'Last Name',
            'First Name',
            'Personal Email',
            'G Suite Email',
            'Test Date',
            'NRS_Reading',
            'NRS_Language',
            'NRS_Math'
        ]
        data.append(headers)
        for tabe in tabes:
            student = tabe.student.student
            try:
                g_suite_email = student.elearn_record.g_suite_email
            except ObjectDoesNotExist:
                g_suite_email = ''
            s = [
                'TABE',
                student.WRU_ID,
                student.last_name,
                student.first_name,
                student.email,
                g_suite_email,
                tabe.test_date,
                tabe.read_nrs,
                tabe.lang_nrs,
                tabe.math_nrs
            ]
            data.append(s)
        for clas_e in clas_es:
            student = clas_e.student.student
            try:
                g_suite_email = student.elearn_record.g_suite_email
            except ObjectDoesNotExist:
                g_suite_email = ''
            s = [
                'CLAS-E',
                student.WRU_ID,
                student.last_name,
                student.first_name,
                student.email,
                g_suite_email,
                clas_e.test_date,
                clas_e.read_nrs,
            ]
            data.append(s)
        return data
    
    def form_valid(self, form):
        clas_es = Clas_E.objects.select_related().all()
        tabes = Tabe.objects.select_related().all()
        filename = "test_storage_report.csv"
        if form.cleaned_data['from_date'] != "":
            from_date = form.cleaned_data['from_date']
            clas_es = clas_es.filter(test_date__gte=from_date)
            tabes = tabes.filter(test_date__gte=from_date)
        if form.cleaned_data['to_date'] != "":
            to_date = form.cleaned_data['to_date']
            clas_es = clas_es.filter(test_date__lte=to_date)
            tabes = tabes.filter(test_date__lte=to_date)
        data = self.get_data(clas_es, tabes)
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

class EventAttendanceCSV(LoginRequiredMixin, FormView):

    model = TestAppointment
    form_class = DateFilterForm
    template_name = "assessments/event_attendance_csv.html"

    def get_data(self, student_dict):
        data = []
        headers = [
            "PROVIDERID",
            "SID",
            "OTHER_ID",
            "LAST_NAME",
            "FIRST_NAME",
            "MIDDLE_INITIAL",
            "COURSE_ID",
            "COURSE_NAME",
            "Partner",
            "HOURS_1", "HOURS_DATE_1", "HOURS_DL_1",
            "HOURS_2", "HOURS_DATE_2", "HOURS_DL_2",
            "HOURS_3", "HOURS_DATE_3", "HOURS_DL_3",
            "HOURS_4", "HOURS_DATE_4", "HOURS_DL_4", 
            "HOURS_5", "HOURS_DATE_5", "HOURS_DL_5",
            "HOURS_6", "HOURS_DATE_6", "HOURS_DL_6",
            "HOURS_7", "HOURS_DATE_7", "HOURS_DL_7",
            "HOURS_8", "HOURS_DATE_8", "HOURS_DL_8",
            "HOURS_9", "HOURS_DATE_9", "HOURS_DL_9",
            "HOURS_10", "HOURS_DATE_10", "HOURS_DL_10",
            "HOURS_11", "HOURS_DATE_11", "HOURS_DL_11",
            "HOURS_12", "HOURS_DATE_12", "HOURS_DL_12",
            "HOURS_13", "HOURS_DATE_13", "HOURS_DL_13",
            "HOURS_14", "HOURS_DATE_14", "HOURS_DL_14",
            "HOURS_15", "HOURS_DATE_15", "HOURS_DL_15",
            "HOURS_16", "HOURS_DATE_16", "HOURS_DL_16",
            "HOURS_17", "HOURS_DATE_17", "HOURS_DL_17", 
            "HOURS_18", "HOURS_DATE_18", "HOURS_DL_18", 
            "HOURS_19", "HOURS_DATE_19", "HOURS_DL_19",
            "HOURS_20", "HOURS_DATE_20", "HOURS_DL_20",
            "HOURS_21", "HOURS_DATE_21", "HOURS_DL_21",
            "HOURS_22", "HOURS_DATE_22", "HOURS_DL_22",
            "HOURS_23", "HOURS_DATE_23", "HOURS_DL_23",
            "HOURS_24", "HOURS_DATE_24", "HOURS_DL_24",
            "HOURS_25", "HOURS_DATE_25", "HOURS_DL_25",
            "HOURS_26", "HOURS_DATE_26", "HOURS_DL_26",
            "HOURS_27", "HOURS_DATE_27", "HOURS_DL_27",
            "HOURS_28", "HOURS_DATE_28", "HOURS_DL_28",
            "HOURS_29", "HOURS_DATE_29", "HOURS_DL_29",
            "HOURS_30", "HOURS_DATE_30", "HOURS_DL_30",
            "HOURS_31", "HOURS_DATE_31", "HOURS_DL_31",
            "HOURS_32", "HOURS_DATE_32", "HOURS_DL_32",
            "HOURS_33", "HOURS_DATE_33", "HOURS_DL_33",
            "HOURS_34", "HOURS_DATE_34", "HOURS_DL_34",
            "HOURS_35", "HOURS_DATE_35", "HOURS_DL_35",
            "HOURS_36", "HOURS_DATE_36", "HOURS_DL_36",
            "HOURS_37", "HOURS_DATE_37", "HOURS_DL_37",
            "HOURS_38", "HOURS_DATE_38", "HOURS_DL_38",
            "HOURS_39", "HOURS_DATE_39", "HOURS_DL_39",
            "HOURS_40", "HOURS_DATE_40", "HOURS_DL_40",
            "HOURS_41", "HOURS_DATE_41", "HOURS_DL_41",
            "HOURS_42", "HOURS_DATE_42", "HOURS_DL_42",
            "HOURS_43", "HOURS_DATE_43", "HOURS_DL_43",
            "HOURS_44", "HOURS_DATE_44", "HOURS_DL_44", 
            "HOURS_45", "HOURS_DATE_45", "HOURS_DL_45",
            "HOURS_46", "HOURS_DATE_46", "HOURS_DL_46",
            "HOURS_47", "HOURS_DATE_47", "HOURS_DL_47",
            "HOURS_48", "HOURS_DATE_48", "HOURS_DL_48"
        ]
        data.append(headers)
        for item in student_dict:
            s = student_dict[item]
            data.append(s)
        return data

    def form_valid(self, form):
        appts = TestAppointment.objects.filter(attendance_type='P')
        filename = 'event_attendance.csv'
        if form.cleaned_data['from_date'] != "":
            from_date = form.cleaned_data['from_date']
            appts = appts.filter(event__start__gte=from_date)
        if form.cleaned_data['to_date'] != "":
            to_date = form.cleaned_data['to_date']
            appts = appts.filter(event__start__lte=to_date)
        student_dict = {}
        for appt in appts:
            if appt.attendance_date is not None:
                date = appt.attendance_date
            else:
                date = appt.event.start.date()
            record = [
                appt.att_hours,
                date.strftime("%Y%m%d"),
                "N"
            ]
            if appt.student.WRU_ID not in student_dict:
                student = [
                    '9',
                    appt.student.WRU_ID,
                    "",
                    appt.student.last_name,
                    appt.student.first_name,
                    '',
                    '',
                    '',
                    appt.student.partner,
                ]
                student_dict[appt.student.WRU_ID] = student
                student_dict[appt.student.WRU_ID].extend(record)
            else:
                student_dict[appt.student.WRU_ID].extend(record)
        data = self.get_data(student_dict)
        return render_to_csv(data=data, filename=filename)


class StudentHisetListView(StudentTestListView):

    model = HiSET
    template_name = "assessments/student_hiset_list.html"


class StudentHisetAddView(StudentTestAddView):

    model = HiSET
    form_class = HiSetForm
    template_name = "assessments/student_hiset_add.html"

    def form_valid(self, form):
        test = form.save(commit=False)
        submitter = self.request.user
        test.reported_by = submitter
        return super(StudentHisetAddView, self).form_valid(form)


class StudentHisetDetailView(StudentTestDetailView):

    model = HiSET
    template_name = "assessments/student_hiset_detail.html"


class StudentAccuplacerListView(StudentTestListView):

    model = Accuplacer
    template_name = "assessments/student_accuplacer_list.html"


class StudentAccuplacerAddView(StudentTestAddView):

    model = Accuplacer
    form_class = AccuplacerForm
    template_name = "assessments/student_accuplacer_add.html"


class StudentAccuplacerDetailView(StudentTestDetailView):

    model = Accuplacer
    template_name = "assessments/student_accuplacer_detail.html" 


class SendScoreReportView(LoginRequiredMixin, View):

    test_type = None
    redirects = {
        'Tabe': 'assessments:student tabe list',
        'Clas_E': 'assessments:student clas-e list'
    }
    
    def get(self, request, *args, **kwargs):
        send_score_report_link_task.delay(self.kwargs['pk'], self.test_type)
        return HttpResponseRedirect(reverse(self.redirects[self.test_type], kwargs={'slug': self.kwargs['slug']}))
