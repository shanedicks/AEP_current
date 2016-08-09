from django.conf.urls import url
from . import views

student_patterns = [
    url(r'^$', student_list)
]

staff_patterns = [
    url(r'^$', staff_list)
]

urlpatterns = [
    url(r'^Students/', include('student_patterns')),
    url(r'^Staff/', include('staff_patterns'))
]