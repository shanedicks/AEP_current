from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from people.views import NewStudentRegistrationView, RegistrationSuccessView, NewStudentSignupView


admin.site.site_header = 'Greenbean Administration'

urlpatterns = [
    url(r'^$',
        TemplateView.as_view(
            template_name='pages/home.html'
        ),
        name='home'),

    # Django Admin Stuff
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('django.contrib.auth.urls')),

    # Other Stuff
    url(r'^', include('people.urls', namespace='people')),
    url(r'^testing/', include('assessments.urls', namespace='assessments')),
    url(r'^classes/', include('sections.urls', namespace='sections')),
    url(r'^coaching/', include('coaching.urls', namespace='coaching')),
    url(r'^registration/$',
        TemplateView.as_view(
            template_name='pages/registration.html'),
        name='registration'),
    url(r'^registration/new/$',
        NewStudentRegistrationView.as_view(),
        name="new student registration"),
    url(r'^registration/success/$',
        RegistrationSuccessView.as_view(),
        name="registration success")

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('BadRequest!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page Not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
