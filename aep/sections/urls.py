from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.ClassListView.as_view(),
        name='class list'),
    url(r'^(?P<slug>[a-zA-Z0-9]{5})/$',
        views.ClassDetailView.as_view(),
        name='class detail'),
    url(r'^(?P<slug>[a-zA-Z0-9]{5})/enroll-student/$',
        views.EnrollStudentView.as_view(),
        name='enroll student'),
]
