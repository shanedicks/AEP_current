from django.urls import path, re_path, include
from django.views.generic import TemplateView, RedirectView
from assessments.views import StudentEventAttendanceView
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

single_student_paperwork_patterns = [
    re_path(r'^$',
        views.StudentPaperworkDetail.as_view(),
        name='paperwork detail'),
    re_path(r'^ferpa/$',
        views.StudentFerpaView.as_view(),
        name='student ferpa'),
    re_path(r'^contract/$',
        views.StudentContractView.as_view(),
        name='student contract'),
    re_path(r'^testing-agreement/$',
        views.StudentTestAgreementView.as_view(),
        name='student test agreement'),
    re_path(r'^tech-policy/$',
        views.StudentTechPolicyView.as_view(),
        name='student tech policy'),
    re_path(r'^self-disclosure/$',
        views.StudentSelfDisclosureView.as_view(),
        name='student self-disclosure'),
    re_path(r'^writing-sample/$',
        views.StudentWritingSampleView.as_view(),
        name='student writing sample'),
    re_path(r'^update/$',
        views.SignPaperworkView.as_view(),
        name='sign paperwork'),
    re_path(r'^upload-id/$',
        views.PhotoIdUploadView.as_view(),
        name='upload photo id'),
    re_path(r'^send-paperwork-link/$',
        views.SendPaperworkLinkView.as_view(),
        name='send paperwork link'),
    re_path(r'^send-upload-id-link/$',
        views.SendUploadIdLinkView.as_view(),
        name='send upload id link'),
    re_path(r'^link-sent/$',
        views.LinkSentView.as_view(),
        name='link sent'),
    path('upload-eligibility-doc/',
        views.EligibilityDocUploadView.as_view(),
        name='upload eligibility doc'),
]

single_student_patterns = [
    re_path(r'^$',
        views.StudentDetailView.as_view(),
        name='student detail'
        ),
    re_path(r'^attendance/$',
        StudentAttendanceView.as_view(),
        name='student attendance'),
    re_path(r'^attendance/events$',
        StudentEventAttendanceView.as_view(),
        name='student event attendance'),
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
        name="send student schedule"),
    re_path(r'^paperwork/', include(single_student_paperwork_patterns))
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
    path('new-student/',
        views.StudentCreateView.as_view(),
        name='create student'
        ),
    re_path(r'^success/$',
        views.StudentCreateSuccessView.as_view(),
        name='student created'
        ),
    re_path(r'^(?P<slug>[a-zA-Z0-9]{5})/', include(single_student_patterns)),
    path('import/',
        views.ImportWruStudentsView.as_view(),
        name='student import'),
    path('update-eligibility/',
        views.UpdateEligibilityView.as_view(),
        name='update eligibility'),
    path('not-found',
        TemplateView.as_view(template_name='people/student_not_found.html'),
        name='student not found')
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
        views.StaffProspectExportCSV.as_view(),
        name='staff prospect export')
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
    #re_path(r'^create-student/$',
    #    views.StaffProspectCreateStudentView.as_view(),
    #    name='prospect create student'),
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
    re_path(r'^notes/(?P<pk>[0-9]+)/', include(single_note_patterns)),
    path('reports/export/',
        views.ProspectExportCSV.as_view(),
        name='prospect export csv'),
]

prospect_intake_patterns = [
    re_path(r'^success/$',
        views.ProspectSuccessView.as_view(),
        name='prospect success'),
    #re_path(r'^registration-form/$',
    #    views.ProspectCreateStudentWizard.as_view(),
    #    name='prospect intake form'),
    re_path(r'^registration-success/$',
        views.ProspectIntakeSuccessView.as_view(),
        name='prospect intake success')
]

english_orientation_patterns = [
    path('overview/',
        TemplateView.as_view(template_name='orientation/en_overiew.html'),
        name="orientation overview"),
    path('class-types/',
        TemplateView.as_view(template_name='orientation/en_class_types.html'),
        name="orientation class types"),
    path('class-types/ccr',
        TemplateView.as_view(template_name='orientation/en_ccr.html'),
        name="orientation ccr"),
    path('class-types/esl',
        TemplateView.as_view(template_name='orientation/en_esl.html'),
        name="orientation esl"),
    path('class-structure/',
        TemplateView.as_view(template_name='orientation/en_class_structure.html'),
        name="orientation class structure"),
    path('class-structure/online-classes',
        TemplateView.as_view(template_name='orientation/en_online_classes.html'),
        name="orientation online classes"),
    path('class-structure/in-person-classes',
        TemplateView.as_view(template_name='orientation/en_in_person_classes.html'),
        name="orientation in-person classes"),
    path('testing/',
        TemplateView.as_view(template_name='orientation/en_testing.html'),
        name="orientation testing"),
    path('coaching/',
        TemplateView.as_view(template_name='orientation/en_coaching.html'),
        name="orientation coaching"),
    path('paperwork/',
        TemplateView.as_view(template_name='orientation/en_paperwork.html'),
        name="orientation paperwork"),

]

spanish_orientation_patterns = [
    path('overview/',
        TemplateView.as_view(template_name='orientation/es_overiew.html'),
        name="spanish orientation overview"),
    path('class-types/',
        TemplateView.as_view(template_name='orientation/es_class_types.html'),
        name="spanish orientation class types"),
    path('class-types/ccr',
        TemplateView.as_view(template_name='orientation/es_ccr.html'),
        name="spanish orientation ccr"),
    path('class-types/esl',
        TemplateView.as_view(template_name='orientation/es_esl.html'),
        name="spanish orientation esl"),
    path('class-structure/',
        TemplateView.as_view(template_name='orientation/es_class_structure.html'),
        name="spanish orientation class structure"),
    path('class-structure/online-classes',
        TemplateView.as_view(template_name='orientation/es_online_classes.html'),
        name="spanish orientation online classes"),
    path('class-structure/in-person-classes',
        TemplateView.as_view(template_name='orientation/es_in_person_classes.html'),
        name="spanish orientation in-person classes"),
    path('testing/',
        TemplateView.as_view(template_name='orientation/es_testing.html'),
        name="spanish orientation testing"),
    path('coaching/',
        TemplateView.as_view(template_name='orientation/es_coaching.html'),
        name="spanish orientation coaching"),
    path('paperwork/',
        TemplateView.as_view(template_name='orientation/es_paperwork.html'),
        name="spanish orientation paperwork"),
]


orientation_patterns = [
    path('start/',
        TemplateView.as_view(
            template_name="orientation/orientation_start.html"
        ),
        name="orientation start"),
    path('en/', include(english_orientation_patterns)),
    path('es/', include(spanish_orientation_patterns)),
    path('finish/',
        views.OrientationFinishView.as_view(),
        name="orientation finish")
]

urlpatterns = [
    re_path(r'^students/', include(student_patterns)),
    re_path(r'^staff/', include(staff_patterns)),
    re_path(r'^prospects/', include(prospect_patterns)),
    re_path(r'^old-student-intake-form/$',
        views.StudentSignupWizard.as_view(),
        name='student signup'),
    re_path(r'^sign-up/$',
        views.ProspectSignupView.as_view(),
        name='prospect signup'),
    path('next-steps/',
        TemplateView.as_view(template_name='people/minor_prospect_signup_success.html'),
        name='minor prospect success'),
    path('student-intake-form/',
        RedirectView.as_view(pattern_name='people:prospect signup', permanent=False),
        name='student wizard redirect'),
    path('eligibility/',
        TemplateView.as_view(template_name='people/eligibility_selection.html'),
        name='eligibility selection'),
    path('citizenship-verification/',
        TemplateView.as_view(template_name='people/citizenship_verification.html'),
        name='citizenship verification'),
    re_path(r'^partners/$',
        views.PartnerStudentCreateView.as_view(),
        name='partner student create'),
    re_path(r'^intake-success/(?P<pk>[0-9]+)/$',
        views.StudentSignupSuccessView.as_view(),
        name='signup success'),
    re_path(r'^elearn-success/$',
        views.ElearnSignupSuccessView.as_view(),
        name='elearn success'),
    re_path(r'^paperwork-success/$',
        TemplateView.as_view(
            template_name='people/paperwork_success.html'
        ),
        name='paperwork success'),
    re_path(r'^(?P<slug>[a-zA-Z0-9]{5})/',
        include(prospect_intake_patterns)),
    re_path(r'^FERPA/$',
        TemplateView.as_view(
            template_name="people/ferpa.html"
        ),
        name="ferpa"),
    re_path(r'^student-contract/$',
        TemplateView.as_view(
            template_name="people/student_contract.html"
        ),
        name="student contract"),
    re_path(r'^tech-policy/$',
        TemplateView.as_view(
            template_name="people/tech_policy.html"
        ),
        name="technology policy"),
    re_path(r'^testing-agreement/$',
        TemplateView.as_view(
            template_name="people/testing_agreement.html"
        ),
        name="testing agreement"),
    path('intercession-report/',
        views.IntercessionReportCSV.as_view(),
        name='intercession report'),
    path('minor-student-report/',
        views.MinorStudentReportCSV.as_view(),
        name='minor student report'),
    path('orientation/<slug>/', include(orientation_patterns))
]
