from django.conf.urls import url, include
from . import views


single_student_assessment_patterns = [
    url(r'^$',
        views.StudentTestHistoryView.as_view(),
        name="student test history"),
    url(r'^appt/(?P<pk>[0-9]+)/$',
        views.TestAppointmentDetailView.as_view,
        name='test appointment detail'),
    url(r'^tabe/$',
        views.StudentTabeListView.as_view(),
        name="student tabe list"),
    url(r'^tabe/(?P<pk>[0-9]+)$',
        views.StudentTabeDetailView.as_view(),
        name="student tabe detail"),
    url(r'^clas-e/$',
        views.StudentClasEListView.as_view(),
        name="student clas-e list"),
    url(r'^clas-e/(?P<pk>[0-9]+)$',
        views.StudentClasEDetailView.as_view(),
        name="student clas-e detail"),
    url(r'^hiset-practice/$',
        views.StudentHisetPracticeListView.as_view(),
        name="student hiset practice list"),
    url(r'^hiset-practice/(?P<pk>[0-9]+)$',
        views.StudentHisetPracticeDetailView.as_view(),
        name="student hiset practice detail"),
]

urlpatterns = [
    url(r'^$',
        views.TestingHomeView.as_view(),
        name="testing home"),
    url(r'^events/$',
        views.TestEventListView.as_view(),
        name="test event list"),
    url(r'^events/(?P<pk>[0-9]+)/$',
        views.TestEventDetailView.as_view(),
        name="test event detail"),
    url(r'(?P<slug>[a-zA-Z0-9]{5})/',
        include(single_student_assessment_patterns)),
]
