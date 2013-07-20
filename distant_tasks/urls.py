from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.generic.base import TemplateView
from users.views import LoginView, ManagerHome

admin.autodiscover()

class TemplatePreview(TemplateView):
    def get_template_names(self):
        return [self.args[0], ]

urlpatterns = patterns('',
    # Examples:
    url(r'^t/(.*)$', TemplatePreview.as_view()),
    url(r'^$', ManagerHome.as_view(), name='home'),
    # url(r'^distant_tasks/', include('distant_tasks.foo.urls')),
    url(r'^admin_tools/', include('admin_tools.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^login/$', LoginView.as_view(), name='login'),
)
