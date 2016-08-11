from django.conf.urls import url
from .views import StudentDetailView, StudentListView, StaffDetailView, StaffListView

student_patterns = [
    url(r'^$', StudentListView.as_view(), name='student_list')
]

staff_patterns = [
    url(r'^$', StaffListView.as_view(), name='staff_list')
]

urlpatterns = [
    url(r'^Students/', include('student_patterns')),
    url(r'^Staff/', include('staff_patterns'))
]