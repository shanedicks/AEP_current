from django.conf.urls import url, include
from . import views


single_class_attendance_patterns = [
    url(r'^$',
        views.AttendanceOverview.as_view(),
        name='attendance overview'),
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


single_class_patterns = [
    url(r'^$',
        views.ClassDetailView.as_view(),
        name='class detail'),
    url(r'^add-student/$',
        views.AddStudentView.as_view(),
        name='add student'),
    url(r'^attendance/',
        include(single_class_attendance_patterns))
]

staff_patterns = [

]

student_patterns = [
    url(r'^$',
        views.StudentClassListView.as_view(),
        name='student classes'),
    url(r'^print-schedule/$',
        views.StudentScheduleView.as_view(),
        name='print schedule'),
    url(r'^add-class/$',
        views.AddClassView.as_view(),
        name='add class')
   # url(r'^add-section/$',
   #     views.AddClassListView.as_view(),
   #     name='add section list'),
   # url(r'^add-section/(?P<pk>[0-9]{2})/$',
   #     views.AddClassFromListView.as_view(),
   #     name='add-section')
]

enrollment_patterns = [
    url(r'(?P<pk>[0-9]+)/$',
        views.EnrollmentView.as_view(),
        name='enrollment detail'),
    url(r'(?P<pk>[0-9]+)/remove/$',
        views.EnrollmentDeleteView.as_view(),
        name='delete enrollment'),
]

urlpatterns = [
    url(r'^$',
        views.ClassListView.as_view(),
        name='class list'),
    url(r'^enrollments/',
        include(enrollment_patterns)),
    url(r'^teaching/',
        include(staff_patterns)),
    url(r'^my-classes/',
        include(student_patterns)),
    url(r'^(?P<slug>[a-zA-Z0-9]{5})/',
        include(single_class_patterns))
]
