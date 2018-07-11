from django.conf.urls import url
from . import views

app_name = 'semesters'

urlpatterns = [
    url(r'^$',
        views.SemesterListView.as_view(),
        name='semester list'),
    url(r'^(?P<pk>\d+)/$',
        views.SemesterDetailView.as_view(),
        name='semester detail'),
]
