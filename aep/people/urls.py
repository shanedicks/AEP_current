from django.conf.urls import url, include
from . import views

single_student_patterns = [
    url(r'^$',
        views.StudentDetailView.as_view(),
        name='student detail'
        ),
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
    url(r'^', include('sections.urls'))
]

student_patterns = [
    url(r'^$',
        views.StudentListView.as_view(),
        name='student list'
        ),
    url(r'^csv/$',
        views.StudentCSV.as_view(),
        name='student list csv'),
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
    url(r'^new/$',
        views.UserCreateView.as_view(),
        name='create user'),
    url(r'^sign-up/$',
        views.NewStudentSignupView.as_view(),
        name='student signup'),
    url(r'^success/$',
        views.StudentSignupSuccessView.as_view(),
        name='signup success')
]
