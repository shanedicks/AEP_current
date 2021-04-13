from django.conf.urls import url, include
from . import views

app_name = 'sections'

single_class_attendance_patterns = [
    url(r'^$',
        views.AttendanceOverview.as_view(),
        name='attendance overview'),
    url(r'^g-suite/$',
        views.GSuiteAttendanceView.as_view(),
        name='g suite attendance'),
    url(r'^(?P<pk>[0-9]+)/$',
        views.SingleAttendanceView.as_view(),
        name='single attendance'),
    url(r'^(?P<attendance_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$',
        views.DailyAttendanceView.as_view(),
        name='daily attendance'),
    url(r'^(?P<attendance_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/print-sign-in/$',
        views.PrintSignInView.as_view(),
        name='sign in'),
]

single_class_skills_patterns = [
    url(r'^$',
        views.SkillsOverview.as_view(),
        name='skills overview'),
    url(r'^(?P<pk>[0-9]+)/$',
        views.SingleSkillUpdateView.as_view(),
        name='single skill update'),
    url(r'^csv/$',
        views.SectionSkillMasteryCSV.as_view(),
        name='section skill mastery csv')
]


single_class_patterns = [
    url(r'^$',
        views.ClassDetailView.as_view(),
        name='class detail'),
    url(r'^add-student/$',
        views.AddStudentView.as_view(),
        name='add student'),
    url(r'^attendance/',
        include(single_class_attendance_patterns)),
    url(r'^testing-preview/$',
        views.ClassTestingPreview.as_view(),
        name='testing preview'),
    url(r'^skills/',
        include(single_class_skills_patterns)),
    url(r'^csv/$',
        views.ClassRosterCSV.as_view(),
        name='class roster csv')
]

staff_patterns = [

]

enrollment_patterns = [
    url(r'(?P<pk>[0-9]+)/$',
        views.EnrollmentView.as_view(),
        name='enrollment detail'),
    url(r'(?P<pk>[0-9]+)/update/$',
        views.EnrollmentUpdateView.as_view(),
        name='enrollment update'),
    url(r'(?P<pk>[0-9]+)/remove/$',
        views.EnrollmentDeleteView.as_view(),
        name='delete enrollment'),
    url(r'(?P<pk>[0-9]+)/att-add/$',
        views.AdminAttendanceView.as_view(),
        name='create admin attendance'),
]

reports_patterns = [
    url(r'^active-students$',
        views.ActiveStudentCSV.as_view(),
        name='active student csv'),
    url(r'^student-enrollment$',
        views.StudentEnrollmentCSV.as_view(),
        name='student enrollment csv'),
    url(r'^atrium$',
        views.AtriumCSV.as_view(),
        name='atrium csv'),
    url(r'^participation$',
        views.ParticipationReport.as_view(),
        name='participation report')
]

urlpatterns = [
    url(r'^$',
        views.ClassListView.as_view(),
        name='class list'),
    url(r'^reports/',
        include(reports_patterns)),
    url(r'^enrollments/',
        include(enrollment_patterns)),
    url(r'^teaching/',
        include(staff_patterns)),
    url(r'^attendance_csv/$',
        views.AttendanceCSV.as_view(),
        name='attendance csv'),
    url(r'^elearn_attendance/$',
        views.ElearnAttendanceCSV.as_view(),
        name='elearn attendance csv'),
    url(r'^(?P<slug>[a-zA-Z0-9]{5})/',
        include(single_class_patterns))
]
