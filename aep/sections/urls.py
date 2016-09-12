from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^(?P<slug>[a-zA-Z0-9]{5})/$',
        views.ClassDetailView.as_view(),
        name='class detail'),
    url(r'^$', views.ClassListView.as_view(),
        name='class list'),
]
