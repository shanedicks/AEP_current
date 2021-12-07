from datetime import timedelta
from django.views.generic import (View,
    DetailView, ListView, UpdateView,
    CreateView, TemplateView, FormView)
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Max, Q
from django.http import HttpResponseRedirect, Http404
from django.template.loader import get_template
from django.template import Context
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic.detail import SingleObjectMixin
from formtools.wizard.views import SessionWizardView
from assessments.forms import OrientationSignupForm
from core.forms import DateFilterForm
from core.utils import render_to_csv
from core.tasks import send_mail_task, email_multi_alternatives_task
from sections.forms import SectionFilterForm
from .models import Staff, Student, CollegeInterest, WIOA, Prospect, ProspectNote
from .forms import (
    StaffForm, StudentPersonalInfoForm, StudentSearchForm,
    StudentInterestForm, StudentContactForm, SSNForm, REForm,
    EETForm, AdditionalDetailsForm, DisabilityForm, StudentForm,
    UserForm, UserUpdateForm, WioaForm, CollegeInterestForm, PartnerForm,
    StudentComplianceForm, StudentNotesForm, ProspectForm, ProspectStatusForm,
    ProspectLinkStudentForm, ProspectAssignAdvisorForm, ProspectNoteForm)
from .tasks import (intake_retention_report_task, orientation_email_task, 
    prospect_check_duplicate_task, prospect_check_returner_task, prospect_export_task)


class UserCreateView(CreateView):
    model = settings.AUTH_USER_MODEL
    form_class = UserForm
    success_url = reverse_lazy('people home')
    template_name = 'people/create_user.html'


# <<<<< Student Views >>>>>

class StudentDetailView(LoginRequiredMixin, DetailView):

    model = Student

    def get_context_data(self, **kwargs):
        context = super(StudentDetailView, self).get_context_data(**kwargs)
        if 'coaches' not in context:
            context['coaches'] = self.object.coaches.filter(active=True).order_by('-start_date')
            context.update(kwargs)
        if 'pops' not in context:
            context['pops'] = self.object.pop.all()
            context.update(kwargs)
        return context


class StudentTranscriptView(LoginRequiredMixin, DetailView):

    model = Student
    template_name = 'people/student_transcript.html'

    def get_context_data(self, **kwargs):
        context = super(StudentTranscriptView, self).get_context_data(**kwargs)
        if 'course_completions' not in context:
            context['course_completions'] = self.object.coursecompletions.all()
            context.update(kwargs)
        if 'certificates' not in context:
            context['certificates'] = self.object.certificates.all()
            context.update(kwargs)
        return context


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


class IntakeRetentionCSV(LoginRequiredMixin, FormView):

    model = Student
    form_class = DateFilterForm
    template_name = "people/intake_retention_csv.html"
    success_url = reverse_lazy('report success')

    def form_valid(self, form):
        from_date = form.cleaned_data['from_date']
        to_date = form.cleaned_data['to_date']
        email = self.request.user.email
        intake_retention_report_task.delay(from_date, to_date, email)
        return super().form_valid(form)


class NewStudentCSV(LoginRequiredMixin, FormView):

    model = Student
    form_class = DateFilterForm
    template_name = "people/new_student_csv.html"

    def get_student_data(self, students):
        data = []
        headers = [
            "WRU Id",
            "Last Name",
            "First Name",
            "Intake Date",
            'Partner',
            "DOB",
            "Gender",
            "Address",
            "City",
            "State",
            "Zip",
            "Parish",
            "Email",
            "G Suite",
            "Phone",
            "Alt Phone",
            "Emergency Contact",
            "Emergency Contact Phone"
            "Notes"
        ]
        data.append(headers)
        for student in students:
            try:
                g_suite = student.elearn_record.g_suite_email
            except ObjectDoesNotExist:
                g_suite = "No elearn record found"
            s = [
                student.WRU_ID,
                student.last_name,
                student.first_name,
                str(student.intake_date),
                student.partner,
                str(student.dob),
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
                g_suite,
                student.phone,
                student.alt_phone,
                student.emergency_contact,
                student.ec_phone,
                student.notes
            ]
            data.append(s)
        return data

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
            try:
                orientation_email_task.delay(student.first_name, student.email, orientation.id)
            except ConnectionError:
                pass
        return HttpResponseRedirect(reverse_lazy('people:signup success', kwargs={'pk' : orientation.event.pk}))


class StudentCreateSuccessView(TemplateView):

    template_name = 'people/student_create_success.html'


class StudentSignupSuccessView(TemplateView):

    template_name = 'people/temp_signup_success.html'

    def get_context_data(self, **kwargs):
        context = super(StudentSignupSuccessView, self).get_context_data(**kwargs)
        if 'event' not in context:
            Events = apps.get_model('assessments', 'TestEvent')
            event = Events.objects.get(id=self.kwargs['pk'])
            context['event'] = event
            context.update(kwargs)
        return context


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


class NotesUpdateView(LoginRequiredMixin, UpdateView):

    model = Student
    form_class = StudentNotesForm
    template_name = 'people/edit_notes.html'

# <<<<< Staff Views >>>>>


class StaffDetailView(LoginRequiredMixin, DetailView):

    model = Staff


class StaffHomeView(LoginRequiredMixin, DetailView):

    model = Staff
    template_name = 'people/staff_home.html'


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
                partner=False,
                active=True
            ).order_by(
                'last_name',
                'first_name'
            )
        if 'partners' not in context:
            context['partners'] = Staff.objects.filter(
                partner=True,
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


class ProspectSignupView(CreateView):

    model = Prospect
    form_class = ProspectForm
    template_name = 'people/create_prospect.html'

    def get_success_url(self):
        return reverse_lazy('people:prospect success', kwargs={'slug': self.object.slug})

    def form_valid(self, form):
        self.object = form.save()
        prospect_check_duplicate_task.delay(self.object.id)
        Student = apps.get_model('people', 'Student')
        matches = Student.objects.filter(
            first_name=self.object.first_name,
            last_name=self.object.last_name,
            dob=self.object.dob,
        )
        if matches.exists():
            self.object.returning_student = True
            self.object.save()
        return super().form_valid(form)

class ProspectSuccessView(TemplateView):

    template_name = 'people/prospect_success.html'

    def get_context_data(self, **kwargs):
        prospect = Prospect.objects.get(slug=self.kwargs['slug'])
        context = super(ProspectSuccessView, self).get_context_data(**kwargs)
        context['prospect'] = prospect
        cutoff_date = timezone.now().date() - timedelta(days=6570)
        context['minor'] = prospect.dob >= cutoff_date
        return context


class ProspectIntakeSuccessView(ProspectSuccessView):

    template_name = 'people/prospect_intake_success.html'



class ProspectDetailView(LoginRequiredMixin, DetailView):

    model = Prospect
    form_class = ProspectStatusForm
    template_name = 'people/prospect_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProspectDetailView, self).get_context_data(**kwargs)
        context['notes'] = self.object.notes.all()
        return context
    def get_success_url(self):
        return reverse_lazy('people:prospect detail', kwargs={'pk': self.object.pk})


class ProspectStatusFormView(LoginRequiredMixin, UpdateView):

    model = Prospect
    form_class = ProspectStatusForm
    template_name = 'people/prospect_status.html'

    def get_success_url(self):
        return reverse_lazy('people:prospect detail', kwargs={'pk': self.object.pk})


class ProspectUpdateView(LoginRequiredMixin, UpdateView):

    model = Prospect
    template_name = 'people/prospect_update.html'
    form_class = ProspectForm


class ProspectLinkStudentView(LoginRequiredMixin, UpdateView):

    model = Prospect
    template_name = 'people/prospect_student_link.html'
    form_class = ProspectLinkStudentForm

    def get_form_kwargs(self):
        kwargs = super(ProspectLinkStudentView, self).get_form_kwargs()
        if self.request.GET:
            kwargs.update(self.request.GET)
        return kwargs


class ProspectAssignAdvisorView(LoginRequiredMixin, UpdateView):

    model = Prospect
    template_name = 'people/prospect_assign_advisor.html'
    form_class = ProspectAssignAdvisorForm


class ProspectCreateStudentView(CreateView):

    model = Student
    form_class = StudentForm
    template_name = 'people/prospect_registration_form.html'

    def get_success_url(self):
        return reverse('people:prospect intake success', kwargs={'slug': self.kwargs['slug']})

    def get_prospect(self):
        return Prospect.objects.get(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'prospect' not in context:
            context['prospect'] = self.get_prospect()
        if 'wioa_form' not in context:
            context['wioa_form'] = WioaForm(
                initial = {
                    'native_language': self.get_prospect().primary_language
                }
            )
        return context

    def get_initial(self):
        prospect = self.get_prospect()
        initial = {
            'last_name': prospect.last_name,
            'first_name': prospect.first_name,
            'phone': prospect.phone,
            'email': prospect.email,
            'dob': prospect.dob

        }
        return initial

    def post(self, request, *args, **kwargs):
        prospect = self.get_prospect()
        student_form = StudentForm(request.POST)
        wioa_form = WioaForm(request.POST)
        if student_form.is_valid() and wioa_form.is_valid():
            student = student_form.save(commit=False)
            student.save()
            wioa = wioa_form.save(commit=False)
            wioa.student = student
            wioa.save()
            prospect.student = student
            prospect.active = True
            prospect.duplicate = False
            prospect.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            self.object = None
            return self.render_to_response(
                self.get_context_data(
                    wioa_form=wioa_form,
                )
            )


class StaffProspectCreateStudentView(LoginRequiredMixin, ProspectCreateStudentView):

    template_name = 'people/prospect_student_create.html'

    def get_success_url(self):
        return reverse('people:prospect detail', kwargs={'pk': self.kwargs['pk']})

    def get_prospect(self):
        return Prospect.objects.get(pk=self.kwargs['pk'])


class ProspectListView(LoginRequiredMixin, ListView, FormView):

    model = Prospect
    form_class = StudentSearchForm
    template_name = 'people/prospect_list.html'
    context_object_name = 'prospects'
    paginate_by = 25
    status = "All"

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = self.status
        return context


class UnassignedProspectListView(ProspectListView):

    queryset = Prospect.objects.filter(
        active=True,
        advisor=None,
        duplicate=False,
        returning_student=False,
    ).order_by('registration_date')
    status = 'Unassigned'


class ReturningProspectListView(ProspectListView):

    queryset = Prospect.objects.filter(
        active=True,
        duplicate=False,
        returning_student=True
    ).order_by('registration_date')
    status = 'Returning'


class ActiveProspectListView(ProspectListView):

    queryset = Prospect.objects.filter(active=True, duplicate=False).exclude(advisor=None)
    status = 'Active'


class InactiveProspectListView(ProspectListView):

    queryset = Prospect.objects.filter(
        active=False,
        student=None,
        duplicate=False,
        for_credit=False
    )
    status = 'Inactive'


class ClosedProspectListView(ProspectListView):

    queryset = Prospect.objects.filter(active=False).exclude(student=None) | Prospect.objects.filter(for_credit=True)
    status = 'Closed'

class DuplicateProspectListView(ProspectListView):

    queryset = Prospect.objects.filter(duplicate=True, student=None)
    status = "Probable Duplicate"

class StaffProspectListView(ProspectListView):

    template_name = 'people/staff_prospect_list.html'
    status = 'All'
    
    def get_queryset(self): 
        return Prospect.objects.filter(
            advisor__slug=self.kwargs['slug'],
            duplicate=False
        ).annotate(
            contact_count=Count('notes'),
            latest_contact=Max('notes__contact_date')
        ).order_by('contact_count','latest_contact')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['staff'] = Staff.objects.get(slug=self.kwargs['slug'])
        return context


class StaffActiveProspectList(StaffProspectListView):

    status = 'Active'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(active=True)

class StaffInactiveProspectList(StaffProspectListView):

    status = 'Inactive'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(active=False, student=None)


class StaffClosedProspectList(StaffProspectListView):

    status = 'Closed'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(active=False).exclude(student=None)


class ProspectNoteCreateView(LoginRequiredMixin, CreateView):

    model = ProspectNote
    form_class = ProspectNoteForm
    template_name = 'people/prospect_note_form.html'

    def form_valid(self, form):
        note = form.save(commit=False)
        note.prospect = Prospect.objects.get(pk=self.kwargs['pk'])
        note.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('people:prospect detail', kwargs={'pk': self.kwargs['pk']})


class ProspectNoteDetailView(LoginRequiredMixin, DetailView):
    
    model = ProspectNote
    template_name = 'people/prospect_note_detail.html'
    context_object_name = 'note'

class ProspectNoteUpdateView(LoginRequiredMixin, UpdateView):

    model = ProspectNote
    form_class = ProspectNoteForm
    template_name = 'people/prospect_note_form.html'


class ProspectComplianceFormView(LoginRequiredMixin, UpdateView):

    model = Student
    form_class = StudentComplianceForm
    template_name = "people/student_compliance.html"

    def get_object(self):
        return Student.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self):
        return reverse_lazy('people:prospect detail', kwargs={'pk': self.kwargs['pk']})


class ProspectExportCSV(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        staff = apps.get_model('people', 'Staff').objects.get(slug = kwargs['slug'])
        user_email = request.user.email
        prospect_export_task.delay(staff.id, user_email)
        return HttpResponseRedirect(reverse('report success'))


class ProspectMeetingAttendanceCSV(LoginRequiredMixin, FormView):

    model = ProspectNote
    form_class = DateFilterForm
    template_name = 'people/prospect_attendance_csv.html'

    def get_data(self, att_dict):
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
        for item in att_dict:
            s = att_dict[item]
            data.append(s)
        return data

    def form_valid(self, form):
        notes = ProspectNote.objects.filter(successful=True)
        notes = notes.exclude(prospect__student=None)
        filename = 'prospect_note_attendance.csv'
        if form.cleaned_data['from_date'] != "":
            from_date = form.cleaned_data['from_date']
            notes = notes.filter(contact_date__gte=from_date)
        if form.cleaned_data['to_date'] != "":
            to_date = form.cleaned_data['to_date']
            notes = notes.filter(contact_date__lte=to_date)
        prospects = apps.get_model('people', 'Prospect').objects.filter(notes__in=notes).distinct()
        prospect_dict = {}
        for prospect in prospects:
            note = prospect.notes.filter(id__in=notes).latest('contact_date')
            online = "N" if note.contact_method == 'In Person' else "Y" 
            record = [
                '9',
                prospect.student.WRU_ID,
                "",
                prospect.student.last_name,
                prospect.student.first_name,
                "",
                "",
                "",
                prospect.student.partner,
                '1',
                note.contact_date.strftime("%Y%m%d"),
                online
            ]
            prospect_dict[prospect.id] = record
        data = self.get_data(prospect_dict)
        return render_to_csv(data=data, filename=filename)
