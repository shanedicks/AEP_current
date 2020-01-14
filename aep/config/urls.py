from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views


admin.site.site_header = 'Greenbean Administration'

urlpatterns = [
    url(r'^$',
        TemplateView.as_view(
            template_name='pages/home.html'
        ),
        name='home'
    ),
    url(r'^resources/$',
        TemplateView.as_view(
            template_name='pages/resources.html'
        ),
        name='resources'
    ),
    url(r'^reports/$',
        TemplateView.as_view(
            template_name='pages/reports.html'
        ),
        name='reports'
    ),
    url(r'^privacy/$',
        TemplateView.as_view(
            template_name='pages/privacy.html'
        ),
        name='privacy'
    ),

    # Django Admin Stuff
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('django.contrib.auth.urls')),

    # Other Stuff
    url(r'^', include('people.urls', namespace='people')),
    url(r'^testing/', include('assessments.urls')),
    url(r'^classes/', include('sections.urls')),
    url(r'^coaching/', include('coaching.urls')),
    url(r'^sessions/', include('semesters.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('BadRequest!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page Not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
