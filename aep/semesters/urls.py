from django.conf.urls import url, include
from . import views

app_name = 'semesters'


single_semester_patterns = [
    url(r'^$',
        views.SemesterClassListView.as_view(),
        name='semester class list'),
    url(r'^sites-table/$',
        views.SemesterSitesTableView.as_view(),
        name='semester sites table'),
    url(r'^times-table/$',
        views.SemesterTimesTableView.as_view(),
        name='semester times table')
]

urlpatterns = [
    url(r'^$',
        views.SemesterListView.as_view(),
        name='semester list'),
    url(r'^(?P<pk>\d+)/',
        include(single_semester_patterns))
]
