from django.urls import re_path, include
from . import views

app_name = 'sections'

single_class_attendance_patterns = [
    re_path(r'^$',
        views.AttendanceOverview.as_view(),
        name='attendance overview'),
    re_path(r'^g-suite/$',
        views.GSuiteAttendanceView.as_view(),
        name='g suite attendance'),
    re_path(r'^(?P<pk>[0-9]+)/$',
        views.SingleAttendanceView.as_view(),
        name='single attendance'),
    re_path(r'^(?P<attendance_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$',
        views.DailyAttendanceView.as_view(),
        name='daily attendance'),
    re_path(r'^(?P<attendance_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/print-sign-in/$',
        views.PrintSignInView.as_view(),
        name='sign in'),
]

single_class_skills_patterns = [
    re_path(r'^$',
        views.SkillsOverview.as_view(),
        name='skills overview'),
    re_path(r'^(?P<pk>[0-9]+)/$',
        views.SingleSkillUpdateView.as_view(),
        name='single skill update'),
    re_path(r'^csv/$',
        views.SectionSkillMasteryCSV.as_view(),
        name='section skill mastery csv')
]


single_class_patterns = [
    re_path(r'^$',
        views.ClassDetailView.as_view(),
        name='class detail'),
    re_path(r'^add-student/$',
        views.AddStudentView.as_view(),
        name='add student'),
    re_path(r'^attendance/',
        include(single_class_attendance_patterns)),
    re_path(r'^testing-preview/$',
        views.ClassTestingPreview.as_view(),
        name='testing preview'),
    re_path(r'^skills/',
        include(single_class_skills_patterns)),
    re_path(r'^csv/$',
        views.ClassRosterCSV.as_view(),
        name='class roster csv')
]

staff_patterns = [

]

enrollment_patterns = [
    re_path(r'(?P<pk>[0-9]+)/$',
        views.EnrollmentView.as_view(),
        name='enrollment detail'),
    re_path(r'(?P<pk>[0-9]+)/update/$',
        views.EnrollmentUpdateView.as_view(),
        name='enrollment update'),
    re_path(r'(?P<pk>[0-9]+)/remove/$',
        views.EnrollmentDeleteView.as_view(),
        name='delete enrollment'),
    re_path(r'(?P<pk>[0-9]+)/att-add/$',
        views.AdminAttendanceView.as_view(),
        name='create admin attendance'),
]

reports_patterns = [
    re_path(r'^active-students/$',
        views.ActiveStudentCSV.as_view(),
        name='active student csv'),
    re_path(r'^student-enrollment/$',
        views.StudentEnrollmentCSV.as_view(),
        name='student enrollment csv'),
    re_path(r'^atrium/$',
        views.AtriumCSV.as_view(),
        name='atrium csv'),
    re_path(r'^participation/$',
        views.ParticipationReport.as_view(),
        name='participation report'),
    re_path(r'^mondo/$',
        views.MondoAttendanceReport.as_view(),
        name='mondo attendance report')
]

urlpatterns = [
    re_path(r'^$',
        views.ClassListView.as_view(),
        name='class list'),
    re_path(r'^reports/',
        include(reports_patterns)),
    re_path(r'^enrollments/',
        include(enrollment_patterns)),
    re_path(r'^teaching/',
        include(staff_patterns)),
    re_path(r'^attendance_csv/$',
        views.AttendanceCSV.as_view(),
        name='attendance csv'),
    re_path(r'^elearn_attendance/$',
        views.ElearnAttendanceCSV.as_view(),
        name='elearn attendance csv'),
    re_path(r'^(?P<slug>[a-zA-Z0-9]{5})/',
        include(single_class_patterns))
]
