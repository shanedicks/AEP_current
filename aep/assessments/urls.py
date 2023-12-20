from django.urls import path, re_path, include
from . import views

app_name = 'assessments'

single_student_tabe_patterns = [
    re_path(r'^$',
        views.StudentTabeListView.as_view(),
        name="student tabe list"),
    re_path(r'^new/$',
        views.StudentTabeAddView.as_view(),
        name="student tabe add"),
    re_path(r'^(?P<pk>[0-9]+)$',
        views.StudentTabeDetailView.as_view(),
        name="student tabe detail"),
    re_path(r'^(?P<pk>[0-9]+)/score-report-link/$',
        views.TabeScoreReportLinkFormView.as_view(),
        name="tabe score report link"),
    re_path(r'^(?P<pk>[0-9]+)/send-score-report/$',
        views.SendScoreReportView.as_view(test_type = 'Tabe'),
        name="send tabe score report")
]

single_student_clas_e_patterns = [
    re_path(r'^$',
        views.StudentClasEListView.as_view(),
        name="student clas-e list"),
    re_path(r'^new/$',
        views.StudentClasEAddView.as_view(),
        name="student clas-e add"),
    re_path(r'^(?P<pk>[0-9]+)/$',
        views.StudentClasEDetailView.as_view(),
        name="student clas-e detail"),
    re_path(r'^(?P<pk>[0-9]+)/score-report-link/$',
        views.ClasEScoreReportLinkFormView.as_view(),
        name="clas-e score report link"),
    re_path(r'^(?P<pk>[0-9]+)/send-score-report/$',
        views.SendScoreReportView.as_view(test_type="Clas_E"),
        name="send clas-e score report")
]

single_student_gain_patterns = [
    re_path(r'^$',
        views.StudentGainListView.as_view(),
        name="student gain list"),
    re_path(r'^new/$',
        views.StudentGainAddView.as_view(),
        name="student gain add"),
    re_path(r'^(?P<pk>[0-9]+)/$',
        views.StudentGainDetailView.as_view(),
        name="student gain detail"),
]

single_student_hiset_practice_paterns = [
    re_path(r'^$',
        views.StudentHisetPracticeListView.as_view(),
        name="student hiset practice list"),
    re_path(r'^new/$',
        views.StudentHisetPracticeAddView.as_view(),
        name="student hiset practice add"),
    re_path(r'^(?P<pk>[0-9]+)/$',
        views.StudentHisetPracticeDetailView.as_view(),
        name="student hiset practice detail"),
]

single_student_hiset_paterns = [
    re_path(r'^$',
        views.StudentHisetListView.as_view(),
        name="student hiset list"),
    re_path(r'^new/$',
        views.StudentHisetAddView.as_view(),
        name="student hiset add"),
    re_path(r'^(?P<pk>[0-9]+)/$',
        views.StudentHisetDetailView.as_view(),
        name="student hiset detail"),
]

single_student_accuplacer_patterns = [
    re_path(r'^$',
        views.StudentAccuplacerListView.as_view(),
        name="student accuplacer list"),
    re_path(r'^new/$',
        views.StudentAccuplacerAddView.as_view(),
        name="student accuplacer add"),
    re_path(r'^(?P<pk>[0-9]+)/$',
        views.StudentAccuplacerDetailView.as_view(),
        name="student accuplacer detail")
]

single_student_assessment_patterns = [
    re_path(r'^$',
        views.StudentTestHistoryView.as_view(),
        name="student test history"),
    re_path(r'^appointments/$',
        views.TestAppointmentListView.as_view(),
        name='appointment history'),
    re_path(r'^signup/$',
        views.TestingSignupView.as_view(),
        name='test signup'),
    path("upload-hiset-auth/",
        views.HisetAuthUploadView.as_view(),
        name='hiset auth upload'),
    re_path(r'^tabe/',
        include(single_student_tabe_patterns)),
    re_path(r'^clas-e/',
        include(single_student_clas_e_patterns)),
    re_path(r'^hiset/',
        include(single_student_hiset_paterns)),
    re_path(r'^hiset-practice/',
        include(single_student_hiset_practice_paterns)),
    re_path(r'^gain/',
        include(single_student_gain_patterns)),
    re_path(r'^accuplacer/',
        include(single_student_accuplacer_patterns)),
]

report_patterns = [
    re_path(r'^tabe/$',
        views.TabeCSV.as_view(),
        name='tabe csv'),
    re_path(r'^tabe/import$',
        views.TabeImportCSV.as_view(),
        name='tabe_import'),
    re_path(r'^clas-e/$',
        views.ClasECSV.as_view(),
        name='clas-e csv'),
    re_path(r'^clas-e/import$',
        views.ClasEImportCSV.as_view(),
        name='clas-e import'),
    re_path(r'^gain/$',
        views.GainCSV.as_view(),
        name='gain csv'),
    re_path(r'^accelerated-coaching/$',
        views.AcceleratedCoachingReport.as_view(),
        name='accelerated coaching'),
    re_path(r'^event-attendance/$',
        views.EventAttendanceCSV.as_view(),
        name='event attendance csv'),
    re_path(r'^eligibility-report/$',
        views.TestingEligibilityReportView.as_view(),
        name='eligibility report'),
    re_path(r'^test-score-storage/$',
        views.TestScoreStorageCSV.as_view(),
        name='test score storage report')
]

single_event_patterns = [
    re_path(r'^$',
        views.TestEventDetailView.as_view(),
        name="test event detail"),
    re_path(r'^attendance$',
        views.TestEventAttendanceView.as_view(),
        name='test event attendance'),
    re_path(r'^csv$',
        views.TestEventCSV.as_view(),
        name="test event csv"),
    re_path(r'^TOLcsv$',
        views.TabeOnlineCSV.as_view(),
        name="tabe online csv"),
    re_path(r'^attendance_report$',
        views.TestEventAttendanceReport.as_view(),
        name="test event attendance report"),
    path('paperwork/',
        views.TestEventPaperworkView.as_view(),
        name='test event paperwork'),
    path('add-student/',
        views.AddStudentView.as_view(),
        name='add student')
]

single_appointment_patterns = [
    re_path(r'^$',
        views.TestAppointmentDetailView.as_view(),
        name='test appointment detail'),
    re_path(r'^notes/$',
        views.TestAppointmentNotesView.as_view(),
        name='test appointment notes'),
    re_path(r'^attendance/$',
        views.TestAppointmentAttendanceView.as_view(),
        name='test appointment attendance'),
]

urlpatterns = [
    re_path(r'^$',
        views.TestingHomeView.as_view(),
        name="testing home"),
    re_path(r'^missing-history/$',
        views.NoHistoryView.as_view(),
        name='no history'),
    re_path(r'^appointments/(?P<pk>[0-9]+)/',
        include(single_appointment_patterns)),
    re_path(r'^events/current/$',
        views.CurrentEventListView.as_view(),
        name="current event list"),
    re_path(r'^events/past/$',
        views.PastEventListView.as_view(),
        name="past event list"),
    re_path(r'^events/(?P<pk>[0-9]+)/',
       include(single_event_patterns)),
    re_path(r'^reports/',
        include(report_patterns)),
    re_path(r'(?P<slug>[a-zA-Z0-9]{5})/',
        include(single_student_assessment_patterns)),
]
