from django.conf.urls import url, include
from . import views


single_student_coaching_patterns = [
    url(r'^$',
        views.ProfileDetailView.as_view(),
        name='profile detail'),
    url(r'^new/$',
        views.ProfileCreateView.as_view(),
        name='create profile')
]

urlpatterns = [
    url(r'(?P<slug>[a-zA-Z0-9]{5})/',
        include(single_student_coaching_patterns))
]
