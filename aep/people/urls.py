from django.conf.urls import url, include
from sections.views import StudentClassListView, StudentScheduleView, AddClassView, StudentAttendanceView
from . import views

app_name = 'people'

class_patterns = [
    url(r'^$',
        StudentClassListView.as_view(),
        name='student classes'),
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
    url(r'^college-interest/$',
        views.CollegeInterestDetailView.as_view(),
        name='college interest detail'
        ),
    url(r'^college-interest/new$',
        views.CollegeInterestFormView.as_view(),
        name='college interest form'
        ),
    url(r'^my-classes/', include(class_patterns))
]

student_patterns = [
    url(r'^$',
        views.StudentListView.as_view(),
        name='student list'
        ),
    url(r'^reports/active$',
        views.ActiveStudentCSV.as_view(),
        name='active student csv'),
    url(r'^reports/new$',
        views.NewStudentCSV.as_view(),
        name='new student csv'),
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

urlpatterns = [
    url(r'^students/', include(student_patterns)),
    url(r'^staff/', include(staff_patterns)),
    url(r'^sign-up/$',
        views.StudentSignupWizard.as_view(),
        name='student signup'),
    url(r'^partners/$',
        views.PartnerStudentCreateView.as_view(),
        name='partner student create'),
    url(r'^success/$',
        views.StudentSignupSuccessView.as_view(),
        name='signup success'),
    url(r'^elearn-success/$',
        views.ElearnSignupSuccessView.as_view(),
        name='elearn success'),
]
