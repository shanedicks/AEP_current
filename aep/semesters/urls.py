from django.urls import re_path, include
from . import views

app_name = 'semesters'


single_semester_patterns = [
    re_path(r'^$',
        views.SemesterClassListView.as_view(),
        name='semester class list'),
    re_path(r'^sites-table/$',
        views.SemesterSitesTableView.as_view(),
        name='semester sites table'),
    re_path(r'^times-table/$',
        views.SemesterTimesTableView.as_view(),
        name='semester times table')
]

urlpatterns = [
    re_path(r'^$',
        views.SemesterListView.as_view(),
        name='semester list'),
    re_path(r'^(?P<pk>\d+)/',
        include(single_semester_patterns))
]
