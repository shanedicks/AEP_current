from apiclient import discovery
from datetime import datetime, date
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from django.apps import apps
from django.views.generic import (DetailView, ListView, CreateView,
                                  DeleteView, UpdateView, FormView, View)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db import IntegrityError
from core.forms import DateFilterForm
from core.utils import render_to_csv
from coaching.models import ElearnRecord
from people.models import Student, Staff
from people.forms import StudentSearchForm
from .models import Section, Enrollment, Attendance, Cancellation
from .forms import (SectionFilterForm, ClassAddEnrollmentForm,
                    StudentAddEnrollmentForm, SingleAttendanceForm,
                    AttendanceFormset, SectionSearchForm, AdminAttendanceForm,
                    AttendanceReportForm, EnrollmentReportForm,
                    SingleSkillMasteryForm, SkillMasteryFormset,
                    EnrollmentUpdateForm, CancellationForm)
from .tasks import (participation_detail_task, section_skill_mastery_report_task,
                    mondo_attendance_report_task, cancel_class_task)


class AttendanceCSV(LoginRequiredMixin, FormView):

    model = Attendance
    form_class = AttendanceReportForm
    template_name = "sections/attendance_report_csv.html"

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
        attendance = Attendance.objects.all()
        filename = "attendance_report.csv"
        if form.cleaned_data['semesters'] != "":
            semesters = form.cleaned_data['semesters']
            attendance = attendance.filter(enrollment__section__semester__in=semesters)
        if form.cleaned_data['from_date'] != "":
            from_date = form.cleaned_data['from_date']
            attendance = attendance.filter(attendance_date__gte=from_date)
        if form.cleaned_data['to_date'] != "":
            to_date = form.cleaned_data['to_date']
            attendance = attendance.filter(attendance_date__lte=to_date)
        attendance = attendance.select_related('enrollment__student', 'enrollment__section')
        el = {
            False: 'N',
            True: 'Y'
        }
        att_dict = {}
        for att in attendance:
            record = [
                att.hours,
                att.attendance_date.strftime("%Y%m%d"),
                el[att.online]
            ]
            if att.enrollment.id not in att_dict:
                enrollment = [
                    '9',
                    att.enrollment.student.WRU_ID,
                    "",
                    att.enrollment.student.last_name,
                    att.enrollment.student.first_name,
                    '',
                    att.enrollment.section.WRU_ID,
                    att.enrollment.section.title,
                    att.enrollment.student.partner,
                ]
                att_dict[att.enrollment.id] = enrollment
                att_dict[att.enrollment.id].extend(record)
            else:
                att_dict[att.enrollment.id].extend(record)
        data = self.get_data(att_dict)
        return render_to_csv(data=data, filename=filename)


class ActiveStudentCSV(LoginRequiredMixin, FormView):

    model = Enrollment
    form_class = SectionFilterForm
    template_name = "sections/active_student_csv.html"

    def get_student_data(self, students):
        data = []
        headers = [
            "WRU Id",
            "Last Name",
            "First Name",
            "Intake Date",
            'Partner',
            "DOB",
            "Test Assignment",
            "Gender",
            "Address",
            "City",
            "State",
            "Zip",
            "Parish",
            "Email",
            'G Suite Email',
            "Phone",
            "Alt Phone",
            "Emergency Contact",
            "Emergency Contact Phone",
            "Paperwork",
            "Folder",
            "Orientation",
            "Notes"
        ]
        data.append(headers)

        for student in students:
            try:
                test_assignment = student.student.tests.test_assignment
            except ObjectDoesNotExist:
                test_assignment = ''
            try:
                g_suite = student.student.elearn_record.g_suite_email
            except ObjectDoesNotExist:
                g_suite = "No elearn record found"
            s = [
                student.student.WRU_ID,
                student.student.last_name,
                student.student.first_name,
                str(student.student.intake_date),
                student.student.partner,
                str(student.student.dob),
                test_assignment,
                student.student.get_gender_display(),
                " ".join([
                    student.student.street_address_1,
                    student.student.street_address_2
                ]),
                student.student.city,
                student.student.state,
                student.student.zip_code,
                student.student.get_parish_display(),
                student.student.email,
                g_suite,
                student.student.phone,
                student.student.alt_phone,
                student.student.emergency_contact,
                student.student.ec_phone,
                student.student.get_paperwork_display(),
                student.student.get_folder_display(),
                student.student.get_orientation_display(),
                student.student.notes
            ]
            data.append(s)
        return data

    def form_valid(self, form):
        students = Enrollment.objects.filter(status="A")
        filename = "student_list.csv"
        if form.cleaned_data['site'] is not None:
            site = form.cleaned_data['site']
            students = students.filter(section__site=site)
            filename = "_".join([site.code, filename])
        if form.cleaned_data['program'] != "":
            program = form.cleaned_data['program']
            students = students.filter(section__program=program)
            filename = "_".join([program, filename])

        students = students.distinct('student').select_related('student__tests')
        data = self.get_student_data(students)
        return render_to_csv(data=data, filename=filename)


class StudentEnrollmentCSV(LoginRequiredMixin, FormView):

    model = Enrollment
    form_class = EnrollmentReportForm
    template_name = "sections/student_enrollment_csv.html"

    def get_student_data(self, students):
        data = []
        headers = [
            "WRU Id",
            "Last Name",
            "First Name",
            "Intake Date",
            "Session",
            "Status",
            "Test Assignment",
            "Last Tested",
            'Partner',
            "DOB",
            "Gender",
            "Address",
            "City",
            "State",
            "Zip",
            "Parish",
            "Email",
            'G Suite Email',
            "Phone",
            "Alt Phone",
            "Paperwork",
            "Folder",
            "Orientation",
            "Notes"
        ]
        data.append(headers)

        for student in students:
            try:
                tests = student.student.tests
                assignment = tests.test_assignment
                last_test_date = tests.last_test_date
            except ObjectDoesNotExist:
                assignment = 'No Test History'
                last_test_date = ''
            try:
                g_suite = student.student.elearn_record.g_suite_email
            except ObjectDoesNotExist:
                g_suite = "No elearn record found"

            s = [
                student.student.WRU_ID,
                student.student.last_name,
                student.student.first_name,
                str(student.student.intake_date),
                student.section.semester,
                student.get_status_display(),
                assignment,
                last_test_date,
                student.student.partner,
                str(student.student.dob),
                student.student.get_gender_display(),
                " ".join([
                    student.student.street_address_1,
                    student.student.street_address_2
                ]),
                student.student.city,
                student.student.state,
                student.student.zip_code,
                student.student.get_parish_display(),
                student.student.email,
                g_suite,
                student.student.phone,
                student.student.alt_phone,
                student.student.get_paperwork_display(),
                student.student.get_folder_display(),
                student.student.get_orientation_display(),
                student.student.notes
            ]
            data.append(s)
        return data

    def form_valid(self, form):
        students = Enrollment.objects.all()
        filename = "student_list.csv"
        if form.cleaned_data['semesters'] != "":
            semesters = form.cleaned_data['semesters']
            students = students.filter(section__semester__in=semesters)
        if form.cleaned_data['site'] is not None:
            site = form.cleaned_data['site']
            students = students.filter(section__site=site)
            filename = "_".join([site.code, filename])
        if form.cleaned_data['program'] != "":
            program = form.cleaned_data['program']
            students = students.filter(section__program=program)
            filename = "_".join([program, filename])
        students = students.distinct('student').select_related('student__tests')
        data = self.get_student_data(students)
        return render_to_csv(data=data, filename=filename)


class AtriumCSV(LoginRequiredMixin, FormView):

    model=Enrollment
    form_class = SectionFilterForm
    template_name = "sections/atrium_csv.html"

    def get_student_data(self, students):
        data = []
        headers = [
            "WRU Id",
            "Last Name",
            "First Name",
            "DOB",
            "Gender",
            "Address",
            "City",
            "State",
            "Zip",
            "Parish",
            "Email",
            "Phone",
            "Semester",
            "Course End Date",
            "FA_CRS",
            "FB_CRS",
            "FC_CRS",
            "FD_CRS",
            "FH_CRS",
            "FI_CRS",
            "FJ_CRS",
            "RC01_156",
            "RC01_217",
            "RC01_223",
            "RC01_241",
            "RC01_246"
        ]
        data.append(headers)
        for item in students:
            if students[item]['sites'][6] == 'Y':
                students[item]['sites'][6:] = ['Y','Y','Y','Y','Y','Y',]
            s = []
            s.extend(students[item]['info'])
            s.extend(students[item]['sites'])
            data.append(s)
        return data

    def form_valid(self, form):
        students = Enrollment.objects.filter(status="A", student__partner='').select_related('section__semester')
        filename = "student_list.csv"
        sites_dict = {
            'CH': 1,
            'WB': 2,
            'JP': 3,
            'SC': 5,
            'RC': 6,
        }
        if form.cleaned_data['site'] is not None:
            site = form.cleaned_data['site']
            students = students.filter(section__site=site)
            filename = "_".join([site.code, filename])
        if form.cleaned_data['program'] != "":
            program = form.cleaned_data['program']
            students = students.filter(section__program=program)
            filename = "_".join([program, filename])
        distinct = {}
        for student in students:
            site = student.section.site
            site_index = 0
            if site.code in sites_dict:
                site_index = sites_dict[site.code]
            if student.student.WRU_ID not in distinct:
                distinct[student.student.WRU_ID] = {
                    'info': [
                        student.student.WRU_ID,
                        student.student.last_name,
                        student.student.first_name,
                        str(student.student.dob),
                        student.student.get_gender_display(),
                        " ".join([
                            student.student.street_address_1,
                            student.student.street_address_2
                        ]),
                        student.student.city,
                        student.student.state,
                        student.student.zip_code,
                        student.student.get_parish_display(),
                        student.student.email,
                        student.student.phone,
                        "".join([str(student.section.semester.end_date.year),"50"]),
                        str(student.section.semester.end_date),
                    ],
                    'sites': ['N','N','N','N','N','N','N','N','N','N','N','N',],
                }
                distinct[student.student.WRU_ID]['sites'][site_index] = 'Y'
            else:
                distinct[student.student.WRU_ID]['sites'][site_index] = 'Y'
        data = self.get_student_data(distinct)
        return render_to_csv(data=data, filename=filename)


class ElearnAttendanceCSV(LoginRequiredMixin, FormView):

    model = ElearnRecord
    form_class = AttendanceReportForm
    template_name = "sections/elearn_att.html"

    def get_student_data(self, students):
        data = []
        headers = [
            "WRU_ID",
            'G Suite',
            "Last Name",
            "First Name",
            "Coach",
            "Partner",
            "Class",
            "Teacher",
            "Attendance"
        ]

        data.append(headers)

        for student in students:
            s = [
                student['wru'],
                student['g_suite'],
                student['last'],
                student['first'],
                student['coach'],
                student['partner'],
                student['section'],
                student['teacher']
            ]
            for a in student['attendance']:
                att = ["{}".format(a.attendance_date), a.att_hours]
                s.extend(att)
            data.append(s)
        return data

    def form_valid(self, form):
        if form.cleaned_data['semesters'] != "":
            semesters = form.cleaned_data['semesters']
        if form.cleaned_data['from_date'] != "":
            from_date = form.cleaned_data['from_date']
        if form.cleaned_data['to_date'] != "":
            to_date = form.cleaned_data['to_date']
        elearn = ElearnRecord.objects.select_related().all()
        students = []
        for record in elearn:
            try:
                coach = record.student.coaches.filter(coaching_type='elearn').latest('pk').coach
            except ObjectDoesNotExist:
                coach = "None"
            enrollments = record.student.classes.all()
            if semesters:
                enrollments = enrollments.filter(section__semester__in=semesters)
            for e in enrollments:
                attendance = e.attendance.all()
                if from_date:
                    attendance = e.attendance.filter(attendance_date__gte=from_date)
                if to_date:
                    attendance = e.attendance.filter(attendance_date__lte=to_date)
                s = {
                    'wru': record.student.WRU_ID,
                    'g_suite': record.g_suite_email,
                    'last': record.student.last_name,
                    'first': record.student.first_name,
                    'coach': coach,
                    'partner': record.student.partner,
                    'section': e.section.title,
                    'teacher': e.section.teacher,
                    'attendance': attendance
                }
                students.append(s)

        filename = "elearn_attendance.csv"
        data = self.get_student_data(students)
        return render_to_csv(data=data, filename=filename)



class ClassListView(LoginRequiredMixin, ListView, FormView):

    form_class = SectionSearchForm
    model = Section
    template_name = 'sections/class_list.html'
    paginate_by = 20

    queryset = Section.objects.filter(
        semester__end_date__gte=timezone.now().date()
    ).order_by('site', 'program', 'title')

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


class AddClassListView(ClassListView):

    template_name = 'sections/add_class_list.html'


class ClassDetailView(LoginRequiredMixin, DetailView):

    model = Section
    template_name = 'sections/class_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ClassDetailView, self).get_context_data(**kwargs)
        if 'students' not in context:
            context['students'] = self.object.get_all_students(
            ).order_by(
                'student__last_name',
                'student__first_name'
            )
        return context


class ClassRosterCSV(LoginRequiredMixin, View):

    def get_student_data(self, students):
        data = []
        headers = [
            "Partner Org.",
            "Student ID",
            "Student Last Name",
            "Student First Name",
            "Student Middle Initial",
            "Gender",
            "Date of Birth",
            "Intake Date",
            "Email",
            "G Suite Email",
            "Partner",
            "Phone",
            "Alt Phone",
            "Emergency Contact",
            "Emergency Contact Phone"
        ]
        data.append(headers)
        for student in students:
            try:
                g_suite = student.student.elearn_record.g_suite_email
            except ObjectDoesNotExist:
                g_suite = ''

            s = [
                student.student.partner,
                student.student.WRU_ID,
                student.student.last_name,
                student.student.first_name,
                "",
                student.student.get_gender_display(),
                str(student.student.dob),
                student.student.intake_date,
                student.student.email,
                g_suite,
                student.student.partner,
                student.student.phone,
                student.student.alt_phone,
                student.student.emergency_contact,
                student.student.ec_phone
            ]
            data.append(s)
        return data

    def get(self, request, *args, **kwargs):
        section = Section.objects.get(
            slug=self.kwargs['slug'])
        filename = "student_list.csv"
        students = section.students.prefetch_related('student')
        data = self.get_student_data(students)
        return render_to_csv(data=data, filename=filename)


class ClassTestingPreview(ClassDetailView):

    template_name = 'sections/class_testing_preview.html'

    def get_context_data(self, **kwargs):
        context = super(ClassTestingPreview, self).get_context_data(**kwargs)
        context['students'] = self.object.get_active(
        ).order_by(
            'student__last_name',
            'student__first_name'
        )
        return context


class PrintSignInView(LoginRequiredMixin, DetailView):

    model = Section
    template_name = 'sections/print_sign-in.html'

    def get_context_data(self, **kwargs):
        context = super(PrintSignInView, self).get_context_data(**kwargs)
        if 'attendance_date' not in context:
            context['attendance_date'] = self.kwargs['attendance_date']
        if 'active' not in context:
            context['active'] = self.object.get_active(
            ).order_by(
                'student__last_name',
                'student__first_name'
            )
        return context


class StaffClassListView(LoginRequiredMixin, ListView):

    model = Section
    template_name = 'sections/staff_class_list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'staff' not in context:
            context['staff'] = Staff.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context

    def get_queryset(self):
        return Section.objects.filter(
            teacher__slug=self.kwargs['slug']
        ).order_by(
            "-starting",
            "-semester__start_date",
            "tuesday",
            "start_time"
        )


class StudentClassListView(LoginRequiredMixin, ListView):

    model = Enrollment
    template_name = 'sections/student_class_list.html'

    def get_context_data(self, **kwargs):
        context = super(StudentClassListView, self).get_context_data(**kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        if 'today' not in context:
            context['today'] = timezone.localdate()
            context.update(kwargs)
        return context

    def get_queryset(self):
        if 'slug' in self.kwargs:
            slug = self.kwargs['slug']
            return Enrollment.objects.filter(
                student__slug=slug
            ).order_by(
                "-section__starting",
                "-section__semester__start_date",
                "section__tuesday",
                "section__start_time"
            )


class StudentCurrentClassListView(StudentClassListView):

    def get_context_data(self, **kwargs):
        context = super(StudentCurrentClassListView, self).get_context_data(**kwargs)
        if 'past' not in context:
            context['past'] = False
            context.update(kwargs)
        if 'upcoming' not in context:
            context['upcoming'] = self.object_list.filter(
                section__semester__start_date__gt=timezone.localdate()
            ) | self.object_list.filter(
                section__starting__gt=timezone.localdate()
            )
            context.update(kwargs)
        if 'current' not in context:
            context['current'] = self.object_list.filter(
                section__semester__start_date__lte=timezone.localdate()
            ) | self.object_list.filter(
                section__starting__lte=timezone.localdate()
            )
            context.update(kwargs)
        return context

    def get_queryset(self):
        slug = self.kwargs['slug']
        return Student.objects.get(
            slug=slug
        ).current_classes().order_by(
            "-section__starting",
            "-section__semester__start_date",
            "section__tuesday",
            "section__start_time"
        )


class StudentPastClassListView(StudentClassListView):

    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(StudentPastClassListView, self).get_context_data(**kwargs)
        if 'past' not in context:
            context['past'] = True
            context.update(kwargs)
        return context

    def get_queryset(self):
        slug = self.kwargs['slug']
        return Student.objects.get(
            slug=slug
        ).past_classes().order_by(
            "-section__starting",
            "-section__semester__start_date",
            "section__tuesday",
            "section__start_time"
        )


class StudentScheduleView(StudentClassListView):

    template_name = 'sections/student_schedule.html'


class StudentAttendanceView(StudentClassListView):

    template_name = 'sections/student_attendance.html'


class AddStudentView(LoginRequiredMixin, CreateView):

    model = Enrollment
    template_name = 'sections/enroll_student.html'
    form_class = StudentAddEnrollmentForm

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

    def get_form_kwargs(self):
        kwargs = super(AddStudentView, self).get_form_kwargs()
        if self.request.GET:
            kwargs.update(self.request.GET)
        return kwargs

    def get_success_url(self):
        url = self.object.section.get_absolute_url()
        return url

    def get_context_data(self, **kwargs):
        context = super(AddStudentView, self).get_context_data(**kwargs)
        if 'section' not in context:
            context['section'] = Section.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context


class AddClassView(LoginRequiredMixin, CreateView):

    model = Enrollment
    template_name = 'sections/enroll.html'
    form_class = ClassAddEnrollmentForm

    def get_context_data(self, **kwargs):
        context = super(AddClassView, self).get_context_data(**kwargs)
        if 'filter_form' not in context:
            context['filter_form'] = SectionFilterForm()
            context.update(kwargs)
        if 'student' not in context:
            context['student'] = Student.objects.get(slug=self.kwargs['slug'])
            context.update(kwargs)
        return context

    def get_form_kwargs(self):
        kwargs = super(AddClassView, self).get_form_kwargs()
        if self.request.GET:
            kwargs.update(self.request.GET)
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        filter_form = SectionFilterForm(request.GET, None)
        return self.render_to_response(
            self.get_context_data(
                filter_form=filter_form,
                form=form
            )
        )

    def form_valid(self, form):
        enrollment = form.save(commit=False)
        student = Student.objects.get(slug=self.kwargs['slug'])
        creator = self.request.user
        enrollment.student = student
        enrollment.creator = creator
        #if student.tests.last_test_date is None and enrollment.section.program != 'TRANS':
        #    form.add_error(
        #        None,
        #        'This student has no pre-test on record,'
        #        ' and cannot be enrolled at this time.'
        #        ' Please talk to a Site Team Leader about next steps.'
        #    )
        #    return self.form_invalid(form)
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
        return reverse_lazy(
            'people:student current classes',
            kwargs={'slug': self.kwargs['slug']}
        )


class EnrollmentView(LoginRequiredMixin, DetailView):

    model = Enrollment


class EnrollmentUpdateView(LoginRequiredMixin, UpdateView):

    model = Enrollment
    form_class = EnrollmentUpdateForm
    template_name = "sections/enrollment_update.html"


class EnrollmentDeleteView(LoginRequiredMixin, DeleteView):

    model = Enrollment

    def get_success_url(self):
        student = self.object.student
        return reverse_lazy(
            'people:student current classes',
            kwargs={'slug': student.slug}
        )


class AttendanceOverview(LoginRequiredMixin, DetailView):

    model = Section
    template_name = 'sections/attendance_overview.html'

    def get_daily_totals(self, **kwargs):
        Attendance = apps.get_model('sections', 'Attendance')
        section = self.object
        att = Attendance.objects.filter(
            enrollment__section=section,
        )
        dates = self.object.get_class_dates()
        present = [
            att.filter(attendance_date=date, attendance_type='P').count()
            for date
            in dates 
        ]
        absent = [
            att.filter(attendance_date=date, attendance_type='A').count()
            for date
            in dates 
        ]
        return [present, absent]

    def get_context_data(self, **kwargs):
        context = super(AttendanceOverview, self).get_context_data()
        if 'days' not in context:
            context['days'] = self.object.get_class_dates()
        if 'count' not in context:
            context['count'] = self.object.students.all().count()
        if 'daily_present' not in context:
            context['daily_present'] = self.get_daily_totals()[0]
        if 'daily_absent' not in context:
            context['daily_absent'] = self.get_daily_totals()[1]
        if 'active' not in context:
            context['active'] = self.object.get_active(
            ).order_by(
                'student__last_name',
                'student__first_name'
            )
        if 'dropped' not in context:
            context['dropped'] = self.object.get_dropped(
            ).order_by(
                'student__last_name',
                'student__first_name'
            )
        if 'completed' not in context:
            context['completed'] = self.object.get_completed(
            ).order_by(
                'student__last_name',
                'student__first_name'
            )
        if 'waitlist' not in context:
            context['waitlist'] = self.object.get_waiting(
            ).order_by(
                'student__last_name',
                'student__first_name'
            )
        if 'withdrawn' not in context:
            context['withdrawn'] = self.object.get_withdrawn(
            ).order_by(
                'student__last_name',
                'student__first_name'
            )
        if 'summary' not in context:
            context['summary'] = ['ADMIN']
        return context


class SingleAttendanceView(LoginRequiredMixin, UpdateView):

    model = Attendance
    form_class = SingleAttendanceForm

    def get_success_url(self):
        section = self.object.enrollment.section
        return reverse_lazy(
            'sections:attendance overview',
            kwargs={'slug': section.slug}
        )


class AdminAttendanceView(LoginRequiredMixin, CreateView):

    model = Attendance
    template_name = 'sections/attendance_form.html'
    form_class = AdminAttendanceForm

    def get_context_data(self, **kwargs):
        context = super(AdminAttendanceView, self).get_context_data()
        if 'student' not in context:
            context['student'] = Enrollment.objects.get(pk=self.kwargs['pk']).student
        return context

    def form_valid(self, form):
        att = form.save(commit=False)
        enrollment = Enrollment.objects.get(pk=self.kwargs['pk'])
        att.attendance_type = 'P'
        att.enrollment = enrollment
        att.time_in = enrollment.section.start_time
        att.time_out = enrollment.section.end_time
        try:
            att.save()
            return super(AdminAttendanceView, self).form_valid(form)
        except IntegrityError:
            form.add_error(
                'att_hours',
                'These hours may already have been recorded'
            )
            return self.form_invalid(form)

    def get_success_url(self):
        section = Enrollment.objects.get(pk=self.kwargs['pk']).section
        return reverse_lazy(
            'sections:attendance overview',
            kwargs={'slug': section.slug}
        )

class DailyAttendanceView(LoginRequiredMixin, UpdateView):

    model = Attendance
    form_class = SingleAttendanceForm
    template_name = 'sections/daily_attendance.html'
    section = None

    def get_form_queryset(self):
        attendance_date = self.kwargs['attendance_date']
        queryset = Attendance.objects.filter(
            enrollment__section=self.section,
            enrollment__status="A",
            attendance_date=attendance_date
        ).order_by(
            "enrollment__student__last_name",
            "enrollment__student__first_name"
        )
        return queryset

    def get(self, request, *args, **kwargs):
        self.object = None
        self.section = Section.objects.get(slug=self.kwargs['slug'])
        attendance_date = self.kwargs['attendance_date']
        formset = AttendanceFormset(queryset=self.get_form_queryset())
        return self.render_to_response(
            self.get_context_data(
                formset=formset,
                section=self.section,
                attendance_date=attendance_date,
            )
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        self.section = Section.objects.get(slug=self.kwargs['slug'])
        attendance_date = self.kwargs['attendance_date']
        formset = AttendanceFormset(request.POST, queryset=self.get_form_queryset())
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(
                self.get_context_data(
                    formset=formset,
                    section=self.section,
                    attendance_date=attendance_date
                )
            )

    def get_success_url(self):
        section = self.section
        return reverse_lazy(
            'sections:attendance overview',
            kwargs={'slug': section.slug}
        )


class GSuiteAttendanceView(LoginRequiredMixin, DetailView):

    model = Section
    template_name = 'sections/g_suite_attendance.html'

    def get_context_data(self, **kwargs):
        scopes = ['https://www.googleapis.com/auth/classroom.coursework.students']

        credentials = ServiceAccountCredentials._from_parsed_json_keyfile(
            keyfile_dict=settings.KEYFILE_DICT,
            scopes=scopes
        )

        shane = credentials.create_delegated('shane.dicks@elearnclass.org')
        http_auth = shane.authorize(Http())
        service = discovery.build('classroom', 'v1', http=http_auth)
        raw = {}
        for student in self.object.get_all_students():
            if student.student.elearn_record.g_suite_email:
                raw[student] = service.courses(
                ).courseWork().studentSubmissions().list(
                    courseId=self.object.g_suite_id,
                    states='RETURNED',
                    courseWorkId='-',
                    userId=student.student.elearn_record.g_suite_email
                ).execute()
        scores = {}
        for key, value in raw.items():
            scores[key] = []
            subs = value.get('studentSubmissions')
            if subs is not None:
                for sub in subs:
                    scores[key].insert(0,
                        [
                            datetime.strptime(
                                sub['creationTime'].split('T')[0],
                                "%Y-%m-%d"
                            ).date(),
                            sub.get('assignedGrade', 0)
                        ]
                    )
        context = super(GSuiteAttendanceView, self).get_context_data()
        if 'scores' not in context:
            context['scores'] = scores
        return context


class SkillsOverview(LoginRequiredMixin, DetailView):

    model = Section
    template_name = 'sections/skills_overview.html'

    def get_context_data(self, **kwargs):
        context=super(SkillsOverview, self).get_context_data(**kwargs)
        if 'skills' not in context:
            context['skills'] = self.object.course.skills.all()
        if 'active' not in context:
            context['active'] = self.object.get_active(
            ).order_by(
                'student__last_name',
                'student__first_name'
            )
        if 'dropped' not in context:
            context['dropped'] = self.object.get_dropped(
            ).order_by(
                'student__last_name',
                'student__first_name'
            )
        if 'completed' not in context:
            context['completed'] = self.object.get_completed(
            ).order_by(
                'student__last_name',
                'student__first_name'
            )
        if 'waitlist' not in context:
            context['waitlist'] = self.object.get_waiting(
            ).order_by(
                'student__last_name',
                'student__first_name'
            )
        if 'withdrawn' not in context:
            context['withdrawn'] = self.object.get_withdrawn(
            ).order_by(
                'student__last_name',
                'student__first_name'
            )
        return context


class SingleSkillUpdateView(LoginRequiredMixin, UpdateView):

    model = Section
    form_class = SingleSkillMasteryForm
    template_name = 'sections/single_skill_update.html'

    def get_form_queryset(self):
        SkillMastery = apps.get_model('academics', 'SkillMastery')
        students = [
            enrollment.student
            for enrollment
            in self.object.get_all_students()
        ]
        queryset = SkillMastery.objects.filter(
            student__in=students,
            skill=self.skill
        ).order_by(
            "student__last_name",
            "student__first_name"
        )
        return queryset

    def get(self, request, *args, **kwargs):
        self.object = Section.objects.get(slug=self.kwargs['slug'])
        self.skill = apps.get_model('academics', 'Skill').objects.get(pk=self.kwargs['pk'])
        formset = SkillMasteryFormset(queryset=self.get_form_queryset())
        return self.render_to_response(
            self.get_context_data(
                formset=formset,
                section=self.object,
                skill=self.skill
            )
        )

    def post(self, request, *args, **kwargs):
        self.object = Section.objects.get(slug=self.kwargs['slug'])
        self.skill = apps.get_model('academics', 'Skill').objects.get(pk=self.kwargs['pk'])
        formset = SkillMasteryFormset(request.POST, queryset=self.get_form_queryset())
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(
                self.get_context_data(
                    formset=formset,
                    section=self.object,
                    skill=self.skill
                )
            )

    def get_success_url(self):
        section = self.object
        return reverse_lazy(
            'sections:skills overview',
            kwargs={'slug': section.slug}
        )


class ParticipationReport(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        email = request.user.email
        participation_detail_task.delay(email)
        return HttpResponseRedirect(reverse_lazy('report success'))


class SectionSkillMasteryCSV(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        section = Section.objects.get(slug = kwargs['slug'])
        user_email = request.user.email
        section_skill_mastery_report_task.delay(section.id, user_email)
        return HttpResponseRedirect(reverse('report success'))


class MondoAttendanceReport(LoginRequiredMixin, FormView):

    form_class = AttendanceReportForm
    template_name = "sections/mondo_attendance_report_csv.html"

    def form_valid(self, form):
        email_address = self.request.user.email
        semesters = [s.id for s in form.cleaned_data['semesters']]
        mondo_attendance_report_task.delay(
            email_address=email_address,
            semesters=semesters,
            from_date=form.cleaned_data['from_date'],
            to_date=form.cleaned_data['to_date']
        )
        return HttpResponseRedirect(reverse('report success'))


class CancellationsListView(ListView):

    model = Cancellation
    template_name = 'sections/cancellations_list.html'
    paginate_by = 25
    date_range = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'today' not in context:
            context['today'] = timezone.now().date()
            context.update(kwargs)
        if "date_range" not in context:
            context['date_range'] = self.date_range
            context.update(kwargs)
        return context

    def get_queryset(self):
        today = timezone.now().date()
        querysets = {
            "current": Cancellation.objects.filter(cancellation_date=today),
            "past": Cancellation.objects.filter(cancellation_date__lt=today),
            "future": Cancellation.objects.filter(cancellation_date__gt=today),
        }
        return querysets[self.date_range].order_by(
            "section__site",
            "section__start_time"
        )

class CurrentCancellationsListView(CancellationsListView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'today' not in context:
            context['today'] = timezone.now().date()
            context.update(kwargs)
        return context

    def get_queryset(self):
        today = timezone.now().date()
        return Cancellation.objects.filter(
            cancellation_date=today
        ).order_by(
            "section__site",
            "section__start_time"
        )

class CreateCancellationView(LoginRequiredMixin, CreateView):

    model = Cancellation
    template_name = 'sections/cancel_class.html'
    form_class = CancellationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'attendance_date' in self.kwargs:
            context['today'] = self.kwargs['attendance_date']
        context['section'] = Section.objects.get(slug=self.kwargs['slug'])
        return context

    def get_initial(self):
        initial = {}
        if 'attendance_date' in self.kwargs:
            initial['cancellation_date'] = self.kwargs['attendance_date']
        return initial

    def form_valid(self, form):
        section = Section.objects.get(slug = self.kwargs['slug'])
        user = self.request.user
        cancellation = form.save(commit=False)
        cancellation.section = section
        cancellation.cancelled_by = user
        cancellation.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('sections:confirm cancellation', kwargs={'pk': self.object.pk})


class ConfirmCancellationView(LoginRequiredMixin, DetailView):

    model = Cancellation
    template_name = 'sections/confirm_cancellation.html'


class CancelClassView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        cancellation = Cancellation.objects.get(pk=self.kwargs['pk'])
        cancel_class_task.delay(self.kwargs['pk'])
        return HttpResponseRedirect(reverse(
            'sections:attendance overview',
            kwargs={'slug': cancellation.section.slug}
        ))
