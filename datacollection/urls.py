from dumbdbm import _Database

from django.conf.urls import patterns, url, include

from datacollection import views
from django.contrib.auth.views import login, logout
from datacollection import admin as datacollection_admin
from datacollection.views.admin_utils import SamplesSelect2View
import settings
from django.contrib import admin

from datacollection.models import Papers, Datasets, Samples, Journals, CellLines, CellPops, CellTypes, Conditions,  TissueTypes, Antibodies, DiseaseStates, Platforms
#from ajax_select import urls as ajax_select_urls
import adminactions.urls


from django.db.models.loading import cache as model_cache
from django.contrib.auth.views import login, logout



if not model_cache.loaded:
    model_cache.get_models()


# admin.site = AdminSitePlus()
admin.autodiscover()




urlpatterns = patterns('',
                       url(r'^$', views.main_view_ng),
                       url(r'^new_admin/', include(admin.site.urls)),
                       url(r'^admin/', include(admin.site.urls)),
                       # url(r'^stat/$', DC_stat_view, name="stat"),
                       url(r'^adminactions/', include(include(adminactions.urls))),
                       url(r'^select2/', include('django_select2.urls')),
                       url(r'^select2sample/$', SamplesSelect2View.as_view(),name='SamplesSelect2View'),
                       # url(r'^main$', views.main_view),
                       url(r'^main$', views.main_view_ng),
                       url(r'^main_ng$', views.main_view_ng),
                       url(r'^main_filter_ng$', views.main_filter_ng),
                       url(r'^putative_target_ng', views.target_json),
                       url(r'^motif_ng', views.motif_json),
                       url(r'^file$', views.file_view),
                       # url(r'^putative_target', views.putative_target_view),
                       url(r'^datahub/(?P<dataset_id>[0-9]+)$', views.datahub_view),
                       url(r'^hgtext/(?P<dataset_id>[0-9]+)/$', views.hgtext_view),
                       url(r'^inspector$', views.inspector_ajax),
                       url(r'^accounts/login/$',  login),
                       url(r'^accounts/logout/$', logout),
                       url(r'accounts/check/', views.check_authenticated)
                       )

from django.conf import settings
from django.conf.urls import include, patterns, url

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
                            )
