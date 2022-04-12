from django.urls import re_path, include
from . import views
from .models import AceRecord, ElearnRecord

app_name = 'coaching'


single_student_patterns = [
    re_path(r'^$',
        views.StudentCoachingView.as_view(),
        name='student coaching'),
    re_path(r'^profile/$',
        views.ProfileDetailView.as_view(),
        name='profile detail'),
    re_path(r'^profile/new/$',
        views.ProfileCreateWizard.as_view(),
        name='create profile'),
    re_path(r'^edit/$',
        views.ProfileUpdateWizard.as_view(),
        name='update profile'),
    re_path(r'^assign/$',
        views.CoachingCreateView.as_view(),
        name='coaching create')
]

coachee_list_patterns = [
    re_path(r'^$',
        views.CoacheeListView.as_view(),
        name='coachee list'),
    re_path(r'^active/$',
        views.ActiveCoacheeListView.as_view(),
        name='active coachee list'),
    re_path(r'^inactive/$',
        views.InactiveCoacheeListView.as_view(),
        name='inactive coachee list'),
    re_path(r'^passed-hiset/$',
        views.HisetCoacheeListView.as_view(),
        name='passed hiset coachee list'),
    re_path(r'^ell-to-ccr/$',
        views.EllCcrCoacheeListView.as_view(),
        name='ell to ccr coachee list'),
    re_path(r'^on-hold/$',
        views.OnHoldCoacheeListView.as_view(),
        name='on hold coachee list'),
    re_path(r'^enrolled/$',
        views.EnrolledCoacheeListView.as_view(),
        name='enrolled coachee list'),
]

single_coach_patterns = [
    re_path(r'^coachees/',
        include(coachee_list_patterns)),
    re_path(r'^export$',
        views.CoacheeExportCSV.as_view(),
        name='coachee export'),
    re_path(r'^update-coachings/$',
        views.UpdateCoachingStatusFormsetView.as_view(),
        name='update coachings')
]

single_coaching_patterns = [
    re_path(r'^$',
        views.CoachingDetailView.as_view(),
        name='coaching detail'),
    re_path(r'^meeting/$',
        views.MeetingNoteCreateView.as_view(),
        name='meeting note create'),
    re_path(r'^update-status/$',
        views.UpdateCoachingStatusFormView.as_view(),
        name='update coaching status')
]

coaches_patterns = [
    re_path(r'^(?P<slug>[a-zA-Z0-9]{5})/',
        include(single_coach_patterns)),
]

meetings_patterns = [
    re_path(r'^(?P<pk>[0-9]+)/$',
        views.MeetingNoteDetailView.as_view(),
        name='meeting note detail'),
    re_path(r'^(?P<pk>[0-9]+)/edit/$',
        views.MeetingNoteUpdateView.as_view(),
        name='meeting note update'),
]

ace_patterns = [
    re_path(r'^$',
        views.AceRecordListView.as_view(),
        name='ace record list'),
    re_path(r'^csv/$',
        views.AceRecordCSV.as_view(),
        name='ace record csv'),
    re_path(r'exit-exam/$',
        views.ExitExamCSV.as_view(),
        name='exit exam csv'),
    re_path(r'enrollments/$',
        views.EnrollmentCSV.as_view(model=AceRecord),
        name='ace enrollment csv'),
    re_path(r'^(?P<slug>[a-zA-Z0-9]{5})/$',
        views.AceRecordDetailView.as_view(),
        name='ace record detail'),
    re_path(r'^(?P<slug>[a-zA-Z0-9]{5})/new/$',
        views.AceRecordCreateView.as_view(),
        name='ace record create'),
    re_path(r'^(?P<slug>[a-zA-Z0-9]{5})/edit/$',
        views.AceRecordUpdateView.as_view(),
        name='ace record update')
]

e_learn_patterns = [
    re_path(r'^$',
        views.ElearnRecordListView.as_view(),
        name='elearn record list'),
    re_path(r'^csv/$',
        views.ElearnRecordCSV.as_view(),
        name='elearn record csv'),
    re_path(r'enrollments/$',
        views.EnrollmentCSV.as_view(model=ElearnRecord),
        name='elearn enrollment csv'),
    re_path(r'^(?P<slug>[a-zA-Z0-9]{5})/$',
        views.ElearnRecordDetailView.as_view(),
        name='elearn record detail'),
    re_path(r'^(?P<slug>[a-zA-Z0-9]{5})/new/$',
        views.ElearnRecordCreateView.as_view(),
        name='elearn record create')
]

urlpatterns = [
    re_path(r'^(?P<pk>[0-9]+)/',
        include(single_coaching_patterns)),
    re_path(r'^(?P<slug>[a-zA-Z0-9]{5})/',
        include(single_student_patterns)),
    re_path(r'^coaches/',
        include(coaches_patterns)),
    re_path(r'^meetings/',
        include(meetings_patterns)),
    re_path(r'^ace/',
        include(ace_patterns)),
    re_path(r'^e-learn/',
        include(e_learn_patterns)),
    re_path(r'^export$',
        views.CoachingExportCSV.as_view(),
        name='coaching export')
]
