from django.conf.urls import url, include
from django.views.generic import TemplateView
from sections.views import StudentCurrentClassListView, StudentPastClassListView, StudentScheduleView, AddClassView, StudentAttendanceView
from . import views

app_name = 'people'

class_patterns = [
    url(r'^current/$',
        StudentCurrentClassListView.as_view(),
        name='student current classes'),
    url(r'^past/$',
        StudentPastClassListView.as_view(),
        name='student past classes'),
    url(r'^print-schedule/$',
        StudentScheduleView.as_view(),
        name='print schedule'),
    url(r'^add-class/$',
        AddClassView.as_view(),
        name='add class')
]

single_student_patterns = [
    url(r'^$',
        views.StudentDetailView.as_view(),
        name='student detail'
        ),
    url(r'^attendance/$',
        StudentAttendanceView.as_view(),
        name='student attendance'),
    url(r'^edit/$',
        views.StudentUpdateView.as_view(),
        name='edit student'
        ),
    url(r'^edit-notes/$',
        views.NotesUpdateView.as_view(),
        name='edit notes'
    ),
    url(r'^college-interest/$',
        views.CollegeInterestDetailView.as_view(),
        name='college interest detail'
        ),
    url(r'^college-interest/new$',
        views.CollegeInterestFormView.as_view(),
        name='college interest form'
        ),
    url(r'^compliance/$',
        views.StudentComplianceFormView.as_view(),
        name='student compliance form'),
    url(r'^compliance/(?P<pk>[0-9]+)$',
        views.ProspectComplianceFormView.as_view(),
        name='prospect compliance form'),
    url(r'^transcript/$',
        views.StudentTranscriptView.as_view(),
        name='student transcript'),
    url(r'^my-classes/', include(class_patterns))
]

student_patterns = [
    url(r'^$',
        views.StudentListView.as_view(),
        name='student list'
        ),
    url(r'^reports/new$',
        views.NewStudentCSV.as_view(),
        name='new student csv'),
    url(r'^reports/intake-retention$',
        views.IntakeRetentionCSV.as_view(),
        name='intake retention csv'),
    url(r'^new/$',
        views.StudentCreateView.as_view(),
        name='create student',
        ),
    url(r'^success/$',
        views.StudentCreateSuccessView.as_view(),
        name='student created'
        ),
    url(r'^(?P<slug>[a-zA-Z0-9]{5})/', include(single_student_patterns)),
]


staff_prospect_patterns = [
    url(r'^$',
        views.StaffProspectListView.as_view(),
        name='staff prospects'),
    url(r'^active/$',
        views.StaffActiveProspectList.as_view(),
        name='staff active prospects'),
    url(r'inactive/$',
        views.StaffInactiveProspectList.as_view(),
        name='staff inactive prospects'),
    url(r'closed/$',
        views.StaffClosedProspectList.as_view(),
        name='staff closed prospects'),
]

single_staff_patterns = [
    url(r'^$',
        views.StaffDetailView.as_view(),
        name='staff detail'),
    url(r'^edit/$',
        views.StaffUpdateView.as_view(),
        name='edit staff'),
    url(r'^home/$',
        views.StaffHomeView.as_view(),
        name='staff home'
        ),
    url(r'^prospects/',
        include(staff_prospect_patterns))
]

staff_patterns = [
    url(r'^$',
        views.StaffListView.as_view(),
        name='staff list'),
    url(r'^new/$',
        views.StaffCreateView.as_view(),
        name='create staff'
        ),
    url(r'^(?P<slug>[a-zA-Z0-9]{5})/', include(single_staff_patterns)),
]

single_note_patterns = [
    url(r'^$',
        views.ProspectNoteDetailView.as_view(),
        name='prospect note detail'),
    url(r'^edit/$',
        views.ProspectNoteUpdateView.as_view(),
        name='prospect note edit')
]

single_prospect_patterns = [
    url(r'^$',
        views.ProspectDetailView.as_view(),
        name='prospect detail'),
    url(r'^edit/$',
        views.ProspectUpdateView.as_view(),
        name='edit prospect'),
    url(r'^status/$',
        views.ProspectStatusFormView.as_view(),
        name='prospect update status'),
    url(r'^link-student/$',
        views.ProspectLinkStudentView.as_view(),
        name='prospect link student'),
    url(r'^create-student/$',
        views.ProspectCreateStudentView.as_view(),
        name='prospect create student'),
    url(r'^assign-advisor/$',
        views.ProspectAssignAdvisorView.as_view(),
        name='prospect assign advisor'),
    url(r'^take-note/$',
        views.ProspectNoteCreateView.as_view(),
        name='prospect create note')
]

prospect_patterns = [
    url(r'^$',
        views.ProspectListView.as_view(),
        name='prospect list'),
    url(r'^unassigned/$',
        views.UnassignedProspectListView.as_view(),
        name='unassigned prospect list'),
    url(r'^active/$',
        views.ActiveProspectListView.as_view(),
        name='active prospect list'),
    url(r'^inactive/$',
        views.InactiveProspectListView.as_view(),
        name='inactive prospect list'),
    url(r'^closed/$',
        views.ClosedProspectListView.as_view(),
        name='closed prospect list'),
    url(r'^(?P<pk>[0-9]+)/', include(single_prospect_patterns)),
    url(r'^notes/(?P<pk>[0-9]+)/', include(single_note_patterns))
]

urlpatterns = [
    url(r'^students/', include(student_patterns)),
    url(r'^staff/', include(staff_patterns)),
    url(r'^prospects/', include(prospect_patterns)),
    url(r'^sign-up/$',
        views.StudentSignupWizard.as_view(),
        name='student signup'),
    url(r'^prospect-sign-up/$',
        views.ProspectSignupView.as_view(),
        name='prospect signup'),
    url(r'^partners/$',
        views.PartnerStudentCreateView.as_view(),
        name='partner student create'),
    url(r'^success/(?P<pk>[0-9]+)/$',
        views.StudentSignupSuccessView.as_view(),
        name='signup success'),
    url(r'^elearn-success/$',
        views.ElearnSignupSuccessView.as_view(),
        name='elearn success'),
    url(r'^prospect-success/$',
        TemplateView.as_view(
            template_name='people/prospect_success.html'
        ),
        name='prospect_success'
    ),

]
