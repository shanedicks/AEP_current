from django.conf.urls import url, include
from . import views

app_name = 'assessments'

single_student_tabe_patterns = [
    url(r'^$',
        views.StudentTabeListView.as_view(),
        name="student tabe list"),
    url(r'^new/$',
        views.StudentTabeAddView.as_view(),
        name="student tabe add"),
    url(r'^(?P<pk>[0-9]+)$',
        views.StudentTabeDetailView.as_view(),
        name="student tabe detail"),
    url(r'^(?P<pk>[0-9]+)/score-report-link/$',
        views.TabeScoreReportLinkFormView.as_view(),
        name="tabe score report link")
]

single_student_clas_e_patterns = [
    url(r'^$',
        views.StudentClasEListView.as_view(),
        name="student clas-e list"),
    url(r'^new/$',
        views.StudentClasEAddView.as_view(),
        name="student clas-e add"),
    url(r'^(?P<pk>[0-9]+)/$',
        views.StudentClasEDetailView.as_view(),
        name="student clas-e detail"),
    url(r'^(?P<pk>[0-9]+)/score-report-link/$',
        views.ClasEScoreReportLinkFormView.as_view(),
        name="clas-e score report link")
]

single_student_gain_patterns = [
    url(r'^$',
        views.StudentGainListView.as_view(),
        name="student gain list"),
    url(r'^new/$',
        views.StudentGainAddView.as_view(),
        name="student gain add"),
    url(r'^(?P<pk>[0-9]+)/$',
        views.StudentGainDetailView.as_view(),
        name="student gain detail"),
]

single_student_hiset_practice_paterns = [
    url(r'^$',
        views.StudentHisetPracticeListView.as_view(),
        name="student hiset practice list"),
    url(r'^new/$',
        views.StudentHisetPracticeAddView.as_view(),
        name="student hiset practice add"),
    url(r'^(?P<pk>[0-9]+)/$',
        views.StudentHisetPracticeDetailView.as_view(),
        name="student hiset practice detail"),
]

single_student_hiset_paterns = [
    url(r'^$',
        views.StudentHisetListView.as_view(),
        name="student hiset list"),
    url(r'^new/$',
        views.StudentHisetAddView.as_view(),
        name="student hiset add"),
    url(r'^(?P<pk>[0-9]+)/$',
        views.StudentHisetDetailView.as_view(),
        name="student hiset detail"),
]

single_student_accuplacer_patterns = [
    url(r'^$',
        views.StudentAccuplacerListView.as_view(),
        name="student accuplacer list"),
    url(r'^new/$',
        views.StudentAccuplacerAddView.as_view(),
        name="student accuplacer add"),
    url(r'^(?P<pk>[0-9]+)/$',
        views.StudentAccuplacerDetailView.as_view(),
        name="student accuplacer detail")
]

single_student_assessment_patterns = [
    url(r'^$',
        views.StudentTestHistoryView.as_view(),
        name="student test history"),
    url(r'^appointments/$',
        views.TestAppointmentListView.as_view(),
        name='appointment history'),
    url(r'^signup/$',
        views.TestingSignupView.as_view(),
        name='test signup'),
    url(r'^tabe/',
        include(single_student_tabe_patterns)),
    url(r'^clas-e/',
        include(single_student_clas_e_patterns)),
    url(r'^hiset/',
        include(single_student_hiset_paterns)),
    url(r'^hiset-practice/',
        include(single_student_hiset_practice_paterns)),
    url(r'^gain/',
        include(single_student_gain_patterns)),
    url(r'^accuplacer/',
        include(single_student_accuplacer_patterns)),
]

report_patterns = [
    url(r'^tabe/$',
        views.TabeCSV.as_view(),
        name='tabe csv'),
    url(r'^tabe/import$',
        views.TabeImportCSV.as_view(),
        name='tabe_import'),
    url(r'^clas-e/$',
        views.ClasECSV.as_view(),
        name='clas-e csv'),
    url(r'^clas-e/import$',
        views.ClasEImportCSV.as_view(),
        name='clas-e import'),
    url(r'^gain/$',
        views.GainCSV.as_view(),
        name='gain csv'),
    url(r'^accelerated-coaching/$',
        views.AcceleratedCoachingReport.as_view(),
        name='accelerated coaching'),
    url(r'^event-attendance/$',
        views.EventAttendanceCSV.as_view(),
        name='event attendance csv'),
    url(r'^eligibility-report/$',
        views.TestingEligibilityReportView.as_view(),
        name='eligibility report')
]

single_event_patterns = [
    url(r'^$',
        views.TestEventDetailView.as_view(),
        name="test event detail"),
    url(r'^attendance$',
        views.TestEventAttendanceView.as_view(),
        name='test event attendance'),
    url(r'^csv$',
        views.TestEventCSV.as_view(),
        name="test event csv"),
    url(r'^TOLcsv$',
        views.TabeOnlineCSV.as_view(),
        name="tabe online csv"),
    url(r'^attendance_report$',
        views.TestEventAttendanceReport.as_view(),
        name="test event attendance report")
]

single_appointment_patterns = [
    url(r'^$',
        views.TestAppointmentDetailView.as_view(),
        name='test appointment detail'),
    url(r'^notes/$',
        views.TestAppointmentNotesView.as_view(),
        name='test appointment notes'),
    url(r'^attendance/$',
        views.TestAppointmentAttendanceView.as_view(),
        name='test appointment attendance'),
]

urlpatterns = [
    url(r'^$',
        views.TestingHomeView.as_view(),
        name="testing home"),
    url(r'^missing-history/$',
        views.NoHistoryView.as_view(),
        name='no history'),
    url(r'^appointments/(?P<pk>[0-9]+)/',
        include(single_appointment_patterns)),
    url(r'^events/current/$',
        views.CurrentEventListView.as_view(),
        name="current event list"),
    url(r'^events/past/$',
        views.PastEventListView.as_view(),
        name="past event list"),
    url(r'^events/(?P<pk>[0-9]+)/',
       include(single_event_patterns)),
    url(r'^reports/',
        include(report_patterns)),
    url(r'(?P<slug>[a-zA-Z0-9]{5})/',
        include(single_student_assessment_patterns)),
]
