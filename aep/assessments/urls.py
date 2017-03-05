from django.conf.urls import url, include
from . import views

single_tabe_patterns = [
    url(r'^$',
        views.StudentTabeListView.as_view(),
        name="student tabe list"),
    url(r'^new$',
        views.StudentTabeAddView.as_view(),
        name="student tabe add"),
    url(r'^(?P<pk>[0-9]+)$',
        views.StudentTabeDetailView.as_view(),
        name="student tabe detail")
]

single_clas_e_patterns = [
    url(r'^$',
        views.StudentClasEListView.as_view(),
        name="student clas-e list"),
    url(r'^new$',
        views.StudentClasEAddView.as_view(),
        name="student clas-e add"),
    url(r'^(?P<pk>[0-9]+)$',
        views.StudentClasEDetailView.as_view(),
        name="student clas-e detail"),
]

single_hiset_practice_paterns = [
    url(r'^$',
        views.StudentHisetPracticeListView.as_view(),
        name="student hiset practice list"),
    url(r'^new/$',
        views.StudentHisetPracticeAddView.as_view(),
        name="student hiset practice add"),
    url(r'^/(?P<pk>[0-9]+)$',
        views.StudentHisetPracticeDetailView.as_view(),
        name="student hiset practice detail"),
]

single_student_assessment_patterns = [
    url(r'^$',
        views.StudentTestHistoryView.as_view(),
        name="student test history"),
    url(r'^signup/$',
        views.TestingSignupView.as_view(),
        name='test signup'),
    url(r'^tabe/',
        include(single_tabe_patterns)),
    url(r'^clas-e/',
        include(single_clas_e_patterns)),
    url(r'^hiset-practice/',
        include(single_hiset_practice_paterns)),
    url(r'^hiset-practice/(?P<pk>[0-9]+)$',
        views.StudentHisetPracticeDetailView.as_view(),
        name="student hiset practice detail"),
]

urlpatterns = [
    url(r'^$',
        views.TestingHomeView.as_view(),
        name="testing home"),
    url(r'^appointments/(?P<pk>[0-9]+)/$',
        views.TestAppointmentDetailView.as_view(),
        name='test appointment detail'),
    url(r'^events/$',
        views.TestEventListView.as_view(),
        name="test event list"),
    url(r'^events/(?P<pk>[0-9]+)/$',
        views.TestEventDetailView.as_view(),
        name="test event detail"),
    url(r'(?P<slug>[a-zA-Z0-9]{5})/',
        include(single_student_assessment_patterns)),
]
