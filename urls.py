from django.conf.urls.defaults import *
#import datacollection as datacollection
from datacollection import views
from django.contrib.auth.views import login, logout
import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

PREFIX_URL = settings.PREFIX_URL.lstrip("/")

urlpatterns = patterns('',
              (r'^'+PREFIX_URL+'new_paper_form/$', views.new_paper_form),
              (r'^'+PREFIX_URL+'new_dataset_form/$', views.new_dataset_form),
              (r'^'+PREFIX_URL+'datasets/$', views.datasets),
              (r'^'+PREFIX_URL+'accounts/login/$', login),
              (r'^'+PREFIX_URL+'accounts/logout/$', logout),
              (r'^'+PREFIX_URL+'accounts/register/$', views.register),
              (r'^'+PREFIX_URL+'static/(?P<path>.*)$', 
               'django.views.static.serve',
               {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    # Example:
    # (r'^newdc/', include('newdc.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
