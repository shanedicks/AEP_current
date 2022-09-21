from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, re_path
from django.views.generic import TemplateView
from django.views import defaults as default_views
from sections.views import CurrentCancellationsListView, CancellationsListView


admin.site.site_header = 'Greenbean Administration'

urlpatterns = [
    re_path(r'^$',
        TemplateView.as_view(
            template_name='pages/home.html'
        ),
        name='home'
    ),
    re_path(r'^resources/$',
        TemplateView.as_view(
            template_name='pages/resources.html'
        ),
        name='resources'
    ),
    re_path(r'^reports/$',
        TemplateView.as_view(
            template_name='pages/reports.html'
        ),
        name='reports'
    ),
    re_path(r'^report-success/$',
        TemplateView.as_view(
            template_name='pages/report_success.html'
        ),
        name='report success'
    ),
    re_path(r'^privacy/$',
        TemplateView.as_view(
            template_name='pages/privacy.html'
        ),
        name='privacy'
    ),
    re_path(r'^cancelled/$',
        CurrentCancellationsListView.as_view(),
        name="current cancellations list"
    ),
    re_path(r'^cancelled/all$',
        CancellationsListView.as_view(),
        name="cancellations list"
    ),
    # Django Admin Stuff
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^accounts/', include('django.contrib.auth.urls')),

    # Other Stuff
    re_path(r'^', include('people.urls', namespace='people')),
    re_path(r'^testing/', include('assessments.urls')),
    re_path(r'^classes/', include('sections.urls')),
    re_path(r'^coaching/', include('coaching.urls')),
    re_path(r'^sessions/', include('semesters.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('BadRequest!')}),
        re_path(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        re_path(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page Not Found')}),
        re_path(r'^500/$', default_views.server_error),
    ]
