from django.conf.urls import url, include
from . import views
from .models import AceRecord, ElearnRecord

app_name = 'coaching'


single_student_patterns = [
    url(r'^$',
        views.ProfileDetailView.as_view(),
        name='profile detail'),
    url(r'^new/$',
        views.ProfileCreateWizard.as_view(),
        name='create profile'),
    url(r'^edit/$',
        views.ProfileUpdateWizard.as_view(),
        name='update profile'),
    url(r'^assign/$',
        views.CoachingCreateView.as_view(),
        name='coaching create')
]

single_coach_patterns = [
    url(r'^$',
        views.CoacheeListView.as_view(),
        name='coachee list'),
    url(r'^export$',
        views.CoacheeExportCSV.as_view(),
        name='coachee export')
]

single_coaching_patterns = [
    url(r'^$',
        views.CoachingDetailView.as_view(),
        name='coaching detail'),
    url(r'^meeting/$',
        views.MeetingNoteCreateView.as_view(),
        name='meeting note create'),
]

coaches_patterns = [
    url(r'^(?P<slug>[a-zA-Z0-9]{5})/',
        include(single_coach_patterns)),
    url(r'^(?P<pk>[0-9]+)/',
        include(single_coaching_patterns)),
]

meetings_patterns = [
    url(r'^(?P<pk>[0-9]+)/$',
        views.MeetingNoteDetailView.as_view(),
        name='meeting note detail'),
    url(r'^(?P<pk>[0-9]+)/edit/$',
        views.MeetingNoteUpdateView.as_view(),
        name='meeting note update'),
]

ace_patterns = [
    url(r'^$',
        views.AceRecordListView.as_view(),
        name='ace record list'),
    url(r'^csv/$',
        views.AceRecordCSV.as_view(),
        name='ace record csv'),
    url(r'exit-exam/$',
        views.ExitExamCSV.as_view(),
        name='exit exam csv'),
    url(r'enrollments/$',
        views.EnrollmentCSV.as_view(model=AceRecord),
        name='ace enrollment csv'),
    url(r'^(?P<slug>[a-zA-Z0-9]{5})/$',
        views.AceRecordDetailView.as_view(),
        name='ace record detail'),
    url(r'^(?P<slug>[a-zA-Z0-9]{5})/new/$',
        views.AceRecordCreateView.as_view(),
        name='ace record create')
]

e_learn_patterns = [
    url(r'^$',
        views.ElearnRecordListView.as_view(),
        name='elearn record list'),
    url(r'^csv/$',
        views.ElearnRecordCSV.as_view(),
        name='elearn record csv'),
    url(r'enrollments/$',
        views.EnrollmentCSV.as_view(model=ElearnRecord),
        name='elearn enrollment csv'),
    url(r'^(?P<slug>[a-zA-Z0-9]{5})/$',
        views.ElearnRecordDetailView.as_view(),
        name='elearn record detail'),
    url(r'^(?P<slug>[a-zA-Z0-9]{5})/new/$',
        views.ElearnRecordCreateView.as_view(),
        name='elearn record create')
]

urlpatterns = [
    url(r'^(?P<slug>[a-zA-Z0-9]{5})/',
        include(single_student_patterns)),
    url(r'^coaches/',
        include(coaches_patterns)),
    url(r'^meetings/',
        include(meetings_patterns)),
    url(r'^ace/',
        include(ace_patterns)),
    url(r'^e-learn/',
        include(e_learn_patterns))
]
