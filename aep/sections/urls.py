from django.conf.urls import url, include
from . import views


single_class_patterns = [
    url(r'^$',
        views.ClassDetailView.as_view(),
        name='class detail'),
    url(r'^add-student/$',
        views.AddStudentView.as_view(),
        name='add student'),
]

staff_patterns = [

]

student_patterns = [
    url(r'^$',
        views.StudentClassListView.as_view(),
        name='student classes'),
    url(r'^add-class/$',
        views.AddClassView.as_view(),
        name='add class'),
]

urlpatterns = [
    url(r'^$',
        views.ClassListView.as_view(),
        name='class list'),
    url(r'^classes/',
        include(staff_patterns)),
    url(r'^my-classes/',
        include(student_patterns)),
    url(r'^(?P<slug>[a-zA-Z0-9]{5})/',
        include(single_class_patterns))
]
