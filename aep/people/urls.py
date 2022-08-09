from django.urls import re_path, include
from django.views.generic import TemplateView
from sections.views import (StudentCurrentClassListView,
    StudentPastClassListView, StudentScheduleView, AddClassView,
    StudentAttendanceView, StaffClassListView)
from . import views

app_name = 'people'

student_class_patterns = [
    re_path(r'^current/$',
        StudentCurrentClassListView.as_view(),
        name='student current classes'),
    re_path(r'^past/$',
        StudentPastClassListView.as_view(),
        name='student past classes'),
    re_path(r'^print-schedule/$',
        StudentScheduleView.as_view(),
        name='print schedule'),
    re_path(r'^add-class/$',
        AddClassView.as_view(),
        name='add class')
]

single_student_patterns = [
    re_path(r'^$',
        views.StudentDetailView.as_view(),
        name='student detail'
        ),
    re_path(r'^attendance/$',
        StudentAttendanceView.as_view(),
        name='student attendance'),
    re_path(r'^edit/$',
        views.StudentUpdateView.as_view(),
        name='edit student'
        ),
    re_path(r'^edit-notes/$',
        views.NotesUpdateView.as_view(),
        name='edit notes'
    ),
    re_path(r'^college-interest/$',
        views.CollegeInterestDetailView.as_view(),
        name='college interest detail'
        ),
    re_path(r'^college-interest/new$',
        views.CollegeInterestFormView.as_view(),
        name='college interest form'
        ),
    re_path(r'^compliance/$',
        views.StudentComplianceFormView.as_view(),
        name='student compliance form'),
    re_path(r'^compliance/(?P<pk>[0-9]+)$',
        views.ProspectComplianceFormView.as_view(),
        name='prospect compliance form'),
    re_path(r'^transcript/$',
        views.StudentTranscriptView.as_view(),
        name='student transcript'),
    re_path(r'^my-classes/', include(student_class_patterns)),
    re_path(r'^send-schedule/$',
        views.SendStudentScheduleView.as_view(),
        name="send student schedule")
]

student_patterns = [
    re_path(r'^$',
        views.StudentListView.as_view(),
        name='student list'
        ),
    re_path(r'^reports/new$',
        views.NewStudentCSV.as_view(),
        name='new student csv'),
    re_path(r'^reports/intake-retention$',
        views.IntakeRetentionCSV.as_view(),
        name='intake retention csv'),
    re_path(r'^new/$',
        views.StudentCreateView.as_view(),
        name='create student',
        ),
    re_path(r'^success/$',
        views.StudentCreateSuccessView.as_view(),
        name='student created'
        ),
    re_path(r'^(?P<slug>[a-zA-Z0-9]{5})/', include(single_student_patterns)),
]


staff_prospect_patterns = [
    re_path(r'^$',
        views.StaffProspectListView.as_view(),
        name='staff prospects'),
    re_path(r'^active/$',
        views.StaffActiveProspectList.as_view(),
        name='staff active prospects'),
    re_path(r'inactive/$',
        views.StaffInactiveProspectList.as_view(),
        name='staff inactive prospects'),
    re_path(r'closed/$',
        views.StaffClosedProspectList.as_view(),
        name='staff closed prospects'),
    re_path(r'export/$',
        views.ProspectExportCSV.as_view(),
        name='prospect export')
]


single_staff_patterns = [
    re_path(r'^$',
        views.StaffDetailView.as_view(),
        name='staff detail'),
    re_path(r'^edit/$',
        views.StaffUpdateView.as_view(),
        name='edit staff'),
    re_path(r'^home/$',
        views.StaffHomeView.as_view(),
        name='staff home'
        ),
    re_path(r'^prospects/', include(staff_prospect_patterns)),
    re_path(r'^my-classes/$',
        StaffClassListView.as_view(),
        name='staff class list')
]

staff_patterns = [
    re_path(r'^$',
        views.StaffListView.as_view(),
        name='staff list'),
    re_path(r'^new/$',
        views.StaffCreateView.as_view(),
        name='create staff'
        ),
    re_path(r'^(?P<slug>[a-zA-Z0-9]{5})/', include(single_staff_patterns)),
]

single_note_patterns = [
    re_path(r'^$',
        views.ProspectNoteDetailView.as_view(),
        name='prospect note detail'),
    re_path(r'^edit/$',
        views.ProspectNoteUpdateView.as_view(),
        name='prospect note edit')
]

single_prospect_patterns = [
    re_path(r'^$',
        views.ProspectDetailView.as_view(),
        name='prospect detail'),
    re_path(r'^edit/$',
        views.ProspectUpdateView.as_view(),
        name='edit prospect'),
    re_path(r'^status/$',
        views.ProspectStatusFormView.as_view(),
        name='prospect update status'),
    re_path(r'^link-student/$',
        views.ProspectLinkStudentView.as_view(),
        name='prospect link student'),
    re_path(r'^create-student/$',
        views.StaffProspectCreateStudentView.as_view(),
        name='prospect create student'),
    re_path(r'^assign-advisor/$',
        views.ProspectAssignAdvisorView.as_view(),
        name='prospect assign advisor'),
    re_path(r'^take-note/$',
        views.ProspectNoteCreateView.as_view(),
        name='prospect create note')
]

prospect_patterns = [
    re_path(r'^$',
        views.ProspectListView.as_view(),
        name='prospect list'),
    re_path(r'^unassigned/$',
        views.UnassignedProspectListView.as_view(),
        name='unassigned prospect list'),
    re_path(r'^active/$',
        views.ActiveProspectListView.as_view(),
        name='active prospect list'),
    re_path(r'^inactive/$',
        views.InactiveProspectListView.as_view(),
        name='inactive prospect list'),
    re_path(r'^closed/$',
        views.ClosedProspectListView.as_view(),
        name='closed prospect list'),
    re_path(r'^duplicate/$',
        views.DuplicateProspectListView.as_view(),
        name='duplicate prospect list'),
    re_path(r'^returning/$',
        views.ReturningProspectListView.as_view(),
        name='returning prospect list'),
    re_path(r'^attendance-report/$',
        views.ProspectMeetingAttendanceCSV.as_view(),
        name='prospect meeting attendance csv'),
    re_path(r'^(?P<pk>[0-9]+)/', include(single_prospect_patterns)),
    re_path(r'^notes/(?P<pk>[0-9]+)/', include(single_note_patterns))
]

prospect_intake_patterns = [
    re_path(r'^success/$',
        views.ProspectSuccessView.as_view(),
        name='prospect success'),
    re_path(r'^registration-form/$',
        views.ProspectCreateStudentView.as_view(),
        name='prospect intake form'),
    re_path(r'^registration-success/$',
        views.ProspectIntakeSuccessView.as_view(),
        name='prospect intake success')
]

urlpatterns = [
    re_path(r'^students/', include(student_patterns)),
    re_path(r'^staff/', include(staff_patterns)),
    re_path(r'^prospects/', include(prospect_patterns)),
    re_path(r'^student-intake-form/$',
        views.StudentSignupWizard.as_view(),
        name='student signup'),
    re_path(r'^sign-up/$',
        views.ProspectSignupView.as_view(),
        name='prospect signup'),
    re_path(r'^partners/$',
        views.PartnerStudentCreateView.as_view(),
        name='partner student create'),
    re_path(r'^intake-success/(?P<pk>[0-9]+)/$',
        views.StudentSignupSuccessView.as_view(),
        name='signup success'),
    re_path(r'^elearn-success/$',
        views.ElearnSignupSuccessView.as_view(),
        name='elearn success'),
    re_path(r'^(?P<slug>[a-zA-Z0-9]{5})/',
        include(prospect_intake_patterns))

]
