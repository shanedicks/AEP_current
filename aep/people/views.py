import os
import csv
from apiclient.http import MediaFileUpload
from apiclient.errors import HttpError
from datetime import timedelta, datetime
from io import TextIOWrapper
from django.views.generic import (View,
    DetailView, ListView, UpdateView,
    CreateView, TemplateView, FormView)
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail.message import EmailMessage
from django.db.models import Count, Max, Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import redirect
from django.template.loader import get_template
from django.template import Context
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.generic.detail import SingleObjectMixin
from formtools.wizard.views import SessionWizardView
from assessments.forms import OrientationSignupForm
from core.forms import DateFilterForm, CSVImportForm
from core.utils import render_to_csv, drive_service, file_to_drive, DriveUploadError
from core.tasks import send_mail_task, email_multi_alternatives_task
from sections.forms import SectionFilterForm
from .models import (Staff, Student, CollegeInterest, WIOA, Prospect,
    ProspectNote, Paperwork)
from .forms import (
    StaffForm, StudentPersonalInfoForm, StudentSearchForm,
    StudentInterestForm, StudentContactForm, StudentUpdateForm, SSNForm, REForm,
    EETForm, AdditionalDetailsForm, DisabilityForm, StudentForm,
    UserForm, UserUpdateForm, WioaForm, CollegeInterestForm, PartnerForm,
    StudentComplianceForm, StudentNotesForm, ProspectForm, ProspectStatusForm,
    ProspectLinkStudentForm, ProspectAssignAdvisorForm, ProspectNoteForm, 
    PaperworkForm, PhotoIdForm, EligibilityDocForm)
from .tasks import (intake_retention_report_task, send_orientation_confirmation_task,
    prospect_check_task, prospect_export_task, process_student_import_task,
    send_student_schedule_task, student_link_prospect_task, send_paperwork_link_task,
    student_check_duplicate_task, intercession_report_task, minor_student_report_task, update_eligibility_task)


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
            context['course_completions'] = self.object.coursecompletion_set.all()
            context.update(kwargs)
        if 'certificates' not in context:
            context['certificates'] = self.object.certificate_set.all()
            context.update(kwargs)
        if 'achievements' not in context:
            context['achievements'] = self.object.achievement_set.all()
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
        partners = ['', 'Job1', 'JeffPar']
        self.object_list = self.get_queryset().filter(partner__in=partners)
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
        from_date = form.cleaned_data['from_date'].strftime('%Y-%m-%d')
        to_date = form.cleaned_data['to_date'].strftime('%Y-%m-%d')
        email = self.request.user.email
        intake_retention_report_task.delay(from_date, to_date, email)
        return super().form_valid(form)


class IntercessionReportCSV(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        email = request.user.email
        intercession_report_task.delay(email)
        return HttpResponseRedirect(reverse_lazy('report success'))


class MinorStudentReportCSV(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        email = request.user.email
        minor_student_report_task.delay(email)
        return HttpResponseRedirect(reverse_lazy('report success'))


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
            "Orientation",
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
            "Emergency Contact Phone",
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
                student.get_orientation_display(),
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
    form_class = StudentUpdateForm
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
        site_preference = student_form.cleaned_data['site_preference']
        wf_valid = wioa_form.is_valid()
        if sf_valid and wf_valid:
            student = student_form.save(commit=False)
            student.save()
            student.site_preference.set(site_preference)
            student_link_prospect_task.delay(student.id)
            wioa = wioa_form.save(commit=False)
            wioa.student = student
            wioa.save()
            self.object = student
            student_check_duplicate_task.delay(student.id)
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
        ("contact", StudentContactForm),
        ("race", REForm),
        ("EET", EETForm),
        ("interest", StudentInterestForm),
        ("disability", DisabilityForm),
        ("details", AdditionalDetailsForm),
        ("signup", OrientationSignupForm)
    ]

    template_name = "people/sign_up_wizard.html"

    def get_success_url(self):
        return reverse_lazy('people:signup success', kwargs={'pk' : orientation.event.pk})

    def done(self, form_list, form_dict, **kwargs):
        ssn = self.get_cleaned_data_for_step('ssn')
        personal = self.get_cleaned_data_for_step('personal')
        interest = self.get_cleaned_data_for_step('interest')
        site_preference = interest.pop('site_preference')
        contact = self.get_cleaned_data_for_step('contact')
        race = self.get_cleaned_data_for_step('race')
        eet = self.get_cleaned_data_for_step('EET')
        disability = self.get_cleaned_data_for_step('disability')
        details = self.get_cleaned_data_for_step('details')
        student = Student(**personal, **interest, **contact)
        student.save()
        student_link_prospect_task.delay(student.id)
        student.save()
        student.site_preference.set(site_preference)
        wioa = WIOA(**ssn, **race, **eet, **disability, **details)
        wioa.student = student
        wioa.save()
        orientation = form_dict["signup"].save(commit=False)
        orientation.student = student
        orientation.save()
        student_check_duplicate_task.delay(student.id)
        return HttpResponseRedirect(reverse_lazy('people:signup success', kwargs={'pk' : orientation.event.pk}))


class StudentCreateSuccessView(TemplateView):

    template_name = 'people/student_create_success.html'


class StudentSignupSuccessView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(StudentSignupSuccessView, self).get_context_data(**kwargs)
        if 'event' not in context:
            Events = apps.get_model('assessments', 'TestEvent')
            event = Events.objects.get(id=self.kwargs['pk'])
            if event.test == 'Online Orientation':
                self.template_name = 'people/signup_success_oo.html'
            else:
                self.template_name = 'people/signup_success_ipo.html'
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

    def form_valid(self, form):
        self.object = form.save()
        prospect_check_task.delay(self.object.id)
        age_threshold = timezone.now().date() - timedelta(days=18*365.25)
        print(age_threshold)
        print(self.object.dob)
        if self.object.dob > age_threshold:
            html_message = get_template('emails/minor_signup.html').render()
            message = strip_tags(html_message)
            send_mail_task.delay(
                subject="Urgent Next Steps for Delgado Community College Adult Education Registration!",
                message=message,
                html_message=html_message,
                from_email="welcome@elearnclass.org",
                recipient_list=[self.object.email],
            )
            return HttpResponseRedirect(reverse('people:minor prospect success'))
        else:
            return HttpResponseRedirect("https://wru-intake.lctcs.edu/Home/Index?code=wzawwQLrp+Y=")


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
            student_link_prospect_task.delay(student.id)
            student_check_duplicate_task.delay(student.id)
            return HttpResponseRedirect(self.get_success_url())
        else:
            self.object = None
            return self.render_to_response(
                self.get_context_data(
                    wioa_form=wioa_form,
                )
            )

class ProspectCreateStudentWizard(StudentSignupWizard):

    def get_prospect(self):
        return Prospect.objects.get(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'prospect' not in context:
            context['prospect'] = self.get_prospect()
        return context

    def get_form_initial(self, step):
        prospect = self.get_prospect()
        self.initial_dict = {
            "personal": {
                'last_name': prospect.last_name,
                'first_name': prospect.first_name,
                'email': prospect.email,
                'dob': prospect.dob                
                },
            "contact": {"phone": prospect.phone}
        }
        return self.initial_dict.get(step, {})

    def done(self, form_list, form_dict, **kwargs):
        ssn = self.get_cleaned_data_for_step('ssn')
        personal = self.get_cleaned_data_for_step('personal')
        interest = self.get_cleaned_data_for_step('interest')
        site_preference = interest.pop('site_preference')
        contact = self.get_cleaned_data_for_step('contact')
        race = self.get_cleaned_data_for_step('race')
        eet = self.get_cleaned_data_for_step('EET')
        disability = self.get_cleaned_data_for_step('disability')
        details = self.get_cleaned_data_for_step('details')
        student = Student(**personal, **interest, **contact)
        student.save()
        student.site_preference.set(site_preference)
        student.save()
        student_link_prospect_task.delay(student.id)
        wioa = WIOA(**ssn, **race, **eet, **disability, **details)
        wioa.student = student
        wioa.save()
        orientation = form_dict["signup"].save(commit=False)
        orientation.student = student
        orientation.save()
        student_check_duplicate_task.delay(student.id)
        return HttpResponseRedirect(reverse_lazy('people:signup success', kwargs={'pk' : orientation.event.pk}))



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


class SendStudentScheduleView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        student = Student.objects.get(slug = kwargs['slug'])
        send_student_schedule_task.delay(student.id)
        return HttpResponseRedirect(reverse('people:student current classes', kwargs={'slug': student.slug}))


class SendPaperworkLinkView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        student = Student.objects.get(slug = kwargs['slug'])
        send_paperwork_link_task.delay(student.id, 'sign paperwork')
        return HttpResponseRedirect(reverse('people:link sent', kwargs={'slug': student.slug}))


class SendUploadIdLinkView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        student = Student.objects.get(slug = kwargs['slug'])
        send_paperwork_link_task.delay(student.id, 'upload photo id')
        return HttpResponseRedirect(reverse('people:link sent', kwargs={'slug': student.slug}))


class StudentPaperworkDetail(LoginRequiredMixin, DetailView):

    model = Paperwork
    template_name = "people/student_paperwork_detail.html"

    def get_student(self, **kwargs):
        return Student.objects.get(slug=self.kwargs['slug'])

    def get_object(self):
        student = self.get_student()
        try:
            obj = student.student_paperwork
        except ObjectDoesNotExist:
            student.track()
            obj = student.student_paperwork
        return obj

    def get_context_data(self, **kwargs):
        context = super(StudentPaperworkDetail, self).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = self.get_student(**kwargs)
            context.update(kwargs)
        return context


class LinkSentView(StudentPaperworkDetail):
    template_name = 'people/link_sent.html'

class StudentFerpaView(StudentPaperworkDetail):
    template_name = "people/ferpa.html"


class StudentContractView(StudentPaperworkDetail):
    template_name = "people/student_contract.html"


class StudentTestAgreementView(StudentPaperworkDetail):
    template_name = "people/testing_agreement.html"


class StudentTechPolicyView(StudentPaperworkDetail):
    template_name = "people/tech_policy.html"


class StudentSelfDisclosureView(StudentPaperworkDetail):
    template_name = "people/student_self_disclosure.html"


class StudentWritingSampleView(StudentPaperworkDetail):
    template_name = "people/student_writing_sample.html"


class BasePaperworkView(UpdateView):
    model = Paperwork
    success_url = reverse_lazy('people:paperwork success')

    def get_student_or_redirect(self):
        try:
            student = Student.objects.get(slug=self.kwargs['slug'])

            # Check if the student is a duplicate
            while student.duplicate:
                student = student.duplicate_of

            if student.slug != self.kwargs['slug']:
                # Redirect to the correct URL if the student has changed
                view_name = f"people:{self.request.resolver_match.url_name}"
                return redirect(reverse(view_name, kwargs={'slug': student.slug}))

            return student
        except Student.DoesNotExist:
            return redirect('people:student not found')

    def get_object(self):
        student = self.get_student_or_redirect()
        if isinstance(student, HttpResponseRedirect):
            return student
        try:
            obj = student.student_paperwork
        except ObjectDoesNotExist:
            student.track()
            obj = student.student_paperwork
        return obj

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if isinstance(self.object, HttpResponseRedirect):
            return self.object
        if self.is_paperwork_complete():
            return HttpResponseRedirect(self.success_url)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = self.object.student
        return context

    def is_paperwork_complete(self):
        return False


class SignPaperworkView(BasePaperworkView):

    form_class = PaperworkForm
    template_name = 'people/sign_paperwork.html'

    def is_paperwork_complete(self):
        return self.object.sig_date is not None

    def form_valid(self, form):
        today = timezone.localdate()
        paperwork = form.save(commit=False)
        paperwork.sig_date = today
        if paperwork.guardian_signature != '':
            paperwork.g_sig_date = today
        paperwork.writing = True
        paperwork.disclosure = True
        paperwork.save()

        if 'from' in self.request.POST:
            self.request.GET = self.request.GET.copy()
            self.request.GET['from'] = self.request.POST['from']

        return super().form_valid(form)

    def get_success_url(self):
        source = self.request.POST.get('from')
        
        if source == 'orientation':
            return 'https://docs.google.com/document/d/e/2PACX-1vTr5plBjIrPOHHa2XILcFPznOHM00LRYo_qEOR5QjdwX07Xvl_h61Tmm1Jco_mMoYFjFzIVuz-k0dP9/pub'
        else:
            return self.success_url
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['source'] = self.request.GET.get('from')
        return context


class PhotoIdUploadView(BasePaperworkView):

    form_class = PhotoIdForm
    template_name = 'people/upload_photo_id.html'

    def is_paperwork_complete(self):
        return self.object.pic_id_file != ''

    def form_valid(self, form):
        paperwork = self.object
        photo_id = self.request.FILES['photo_id']
        name = paperwork.student.__str__() + " picture id"
        try:
            paperwork.pic_id_file = file_to_drive(
                name=name, 
                file=photo_id,
                folder_id='1DpE8QKUvuEKMCOaWHiuX4K7f7BGdzHS1'
            )
            paperwork.pic_id = True
            paperwork.save()
            return super().form_valid(form)
        except DriveUploadError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

class EligibilityDocUploadView(LoginRequiredMixin, BasePaperworkView):

    form_class = EligibilityDocForm
    template_name = 'people/upload_eligibility_doc.html'

    def is_paperwork_complete(self):
        return False

    def form_valid(self, form):
        paperwork = self.object
        if 'eligibility_doc' in self.request.FILES:
            eligibility_doc = self.request.FILES['eligibility_doc']
            name = paperwork.student.__str__() + " eligibility documentation"
            try:
                paperwork.eligibility_doc = file_to_drive(
                    name=name, 
                    file=eligibility_doc,
                    folder_id='1LjU_OhXIGeiOhSFULAoUin-agjZwprDH'
                )
            except DriveUploadError as e:
                form.add_error(None, str(e))
                return self.form_invalid(form)

        paperwork.eligibility_verified_by = self.request.user
        paperwork.eligibility_verified_at = timezone.now()
        paperwork.save()
        student = paperwork.student
        student.eligibility_verified = True
        student.save()
        return super().form_valid(form)

    def get_success_url(self):
            return reverse('people:student detail', kwargs={'slug': self.object.student.slug})

class OrientationFinishView(View):

    def get(self, request, *args, **kwargs):
        student = Student.objects.get(slug = kwargs['slug'])
        send_orientation_confirmation_task.delay(student.id)
        student.orientation = 'C'
        student.save()
        return HttpResponseRedirect(reverse('people:sign paperwork', kwargs={'slug': student.slug}))    


class ImportWruStudentsView(LoginRequiredMixin, FormView):

    form_class = CSVImportForm
    template_name = 'people/import_students.html'

    def form_valid(self, form):
        csv_file = self.request.FILES['csv_file']
        decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
        headers = decoded_file.readline().strip().split(",")
        reader = csv.DictReader(decoded_file, fieldnames=headers)
        parish_dict = {k: v for (v, k) in Student.PARISH_CHOICES}
        state_dict = {k.upper(): v for (v, k) in Student.STATE_CHOICES}
        gender_dict = {
            "MALE": 'M',
            "FEMALE": 'F',
            "NON-BINARY": 'B',
            "NO ANSWER": 'N'
        }
        errors = []
        student_ids = []
        for row in reader:
            try:
                dob = datetime.strptime(row['Date of Birth'], '%m/%d/%Y').date()
                student_parish = parish_dict.get(row['Residency Parish'], '37')
                student_state = state_dict.get(row['State'], 'LA')
                student_gender = gender_dict.get(row['Gender'])

                student_data = {
                    'first_name': row['First Name'].title(),
                    'last_name': row['Last Name'].title(),
                    'dob': dob,
                    'phone': row['Telephone No.'],
                    'street_address_1': f"{row['Street 1']} {row['Street 2']}",
                    'city': row['City'],
                    'state': student_state,
                    'parish': student_parish,
                    'gender': student_gender,
                    'zip_code': row['Zip'],
                    'email': row['Email Address'],
                }

                student, created = Student.objects.update_or_create(
                    WRU_ID=row['Student ID'],
                    defaults=student_data
                )

                if created:
                    student_ids.append(student.id)

            except Exception as e:
                row['errors'] = e
                errors.append(row)

        if errors:
            with open('errors.csv', 'w', newline='') as error_file:
                headers.append("errors")
                writer = csv.DictWriter(error_file, fieldnames=headers)
                writer.writeheader()
                for error in errors:
                    writer.writerow(error)
            email = EmailMessage(
                'Student Import Report',
                'These records were not imported',
                'admin@dccaep.org',
                [self.request.user.email]
            )
            email.attach_file('errors.csv')
            email.send()
            os.remove('errors.csv')

        process_student_import_task.delay(self.request.user.email, student_ids)

        return HttpResponseRedirect(reverse('people:student list'))


class UpdateEligibilityView(LoginRequiredMixin, FormView):
    
    form_class = CSVImportForm
    template_name = 'people/update_eligibility.html'
    
    def form_valid(self, form):
        csv_file = self.request.FILES['csv_file']
        decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
        headers = decoded_file.readline().strip().split(",")
        reader = csv.DictReader(decoded_file, fieldnames=headers)
        
        wru_id_list = [row['Student ID'] for row in reader]
        
        # Trigger async task
        update_eligibility_task.delay(wru_id_list, self.request.user.email)
        
        return HttpResponseRedirect(reverse('report success'))
