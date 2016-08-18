from django.conf.urls import url, include
from django.views.generic import TemplateView
from . import views

single_student_patterns = [
    url(r'^$', views.StudentDetailView.as_view(), name='student detail'),
    url(r'^edit/$', views.StudentUpdateView.as_view(), name='edit student'),
]

student_patterns = [
    url(r'^$', views.StudentListView.as_view(), name='student list'),
    url(r'^(?P<slug>[a-zA-Z0-9]{5})/', include(single_student_patterns)),
]

single_staff_patterns = [
    url(r'^$', views.StaffDetailView.as_view(), name='staff detail'),
    url(r'^edit/$', views.StaffUpdateView.as_view(), name='edit staff'),
]

staff_patterns = [
    url(r'^$', views.StaffListView.as_view(), name='staff list'),
    url(r'^(?P<slug>[a-zA-Z0-9]{5})', include(single_staff_patterns)),
]

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='people/home.html'), name='people home'),
    url(r'^students/', include(student_patterns)),
    url(r'^staff/', include(staff_patterns)),
]
