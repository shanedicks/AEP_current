from django.conf.urls import url, include
from . import views


single_student_patterns = [
    url(r'^$',
        views.ProfileDetailView.as_view(),
        name='profile detail'),
    url(r'^new/$',
        views.ProfileCreateView.as_view(),
        name='create profile'),
    url(r'^assign/$',
        views.CoachingCreateView.as_view(),
        name='coaching create')
]

single_coach_patterns = [
    url(r'^(?P<pk>[0-9]+)/$',
        views.CoacheeListView.as_view(),
        name='coachee list'),
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
        views.MeetingNoteUpdateView.as_view,
        name='meeting note update'),
]

ace_patterns = [
    url(r'^(?P<slug>[a-zA-Z0-9]{5})/$',
        views.AceRecordDetailView.as_view(),
        name='ace record detail'),
    url(r'^(?P<slug>[a-zA-Z0-9]{5})/new/$',
        views.AceRecordCreateView.as_view(),
        name='ace record create')
]

urlpatterns = [
    url(r'^(?P<slug>[a-zA-Z0-9]{5})/',
        include(single_student_patterns)),
    url(r'^coaches/',
        include(coaches_patterns)),
    url(r'^meetings/',
        include(meetings_patterns)),
    url(r'^ace/',
        include(ace_patterns))
]
