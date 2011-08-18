from django.conf.urls.defaults import *
from datacollection import views
from django.contrib.auth.views import login, logout
import settings

urlpatterns = patterns('',
              url(r'^$', views.home, name="home"),
              url(r'^papers/(\d+/)?$', views.papers, name="papers"),
              url(r'^weekly_papers/(\d+/)?$',
                  views.weekly_papers, name="weekly_papers"),
              url(r'^samples/(\d+/)?$', views.samples, name="samples"),
              url(r'^weekly_samples/(\d+/)?$',
                  views.weekly_samples, name="weekly_samples"),
              url(r'^samples/$', views.samples, name="samples"),
              url(r'^controls/$', views.controls, name="controls"),
              url(r'^admin/$', views.admin, name="admin"),
              url(r'^report/$', views.report, name="report"),
              url(r'^teams/$', views.teams, name="teams"),
              url(r'^paper_profile/(\d+)/$', views.paper_profile,
                  name="paper_profile"),
              url(r'^dataset_profile/(\d+)/$', views.dataset_profile,
                  name="dataset_profile"),
              url(r'^sample_profile/(\d+)/$', views.sample_profile,
                  name="sample_profile"),
              url(r'^get_samples/(\d+)/$', views.get_samples, 
                  name="get_samples"),
              url(r'^paper_submission/$', views.paper_submission,
                  name="paper_submission"),
              url('^submissions_admin/$', views.submissions_admin,
                  name="submissions_admin"),
              url('^auto_paper_import/$', views.auto_paper_import,
                  name="auto_paper_import"),
              url('^import_samples/(\d+)/$', views.import_samples,
                  name="import_samples"),
              url('^download_paper_samples/(\d+)/$', 
                  views.download_paper_samples, 
                  name="download_paper_samples"),
              url('^upload_sample_form/(\d+)/$', views.upload_sample_form,
                  name="upload_sample_form"),
              url(r'^datasets/$', views.datasets, name="datasets"),
              url(r'^batch_update_datasets/$', views.batch_update_datasets,
                  name="batch_update_datasets"),
              url(r'^batch_update_samples/$', views.batch_update_samples,
                  name="batch_update_samples"),
              #See haystack below
              #url(r'^search/$', views.search, name="search"),
              url(r'^delete_datasets/$', views.delete_datasets,
                  name="delete_datasets"),
              url(r'^delete_papers/$', views.delete_papers,
                  name="delete_papers"),
              url(r'^delete_samples/$', views.delete_samples,
                  name="delete_samples"),                       
              url(r'^stats/$', views.stats, name="stats"),
              url(r'^dcstats/$', views.dcstats, name="dcstats"),
              url(r'^admin_help/(\w+/)?$', views.admin_help,
                  name="admin_help"),
              url(r'^check_raw_files/(\d+)/$', views.check_raw_files,
                  name="check_raw_files"),
              url(r'^run_analysis/(\d+)/$', views.run_analysis,
                  name="run_analysis"),
              url(r'^download_file/(\d+)/$', views.download_file,
                  name="download_file"),
              url(r'^generic_delete/(\w+)/$', views.generic_delete, 
                  name="generic_delete"),
              url(r'^search/$', views.search, name="search"),
              url(r'^front/(\w+)/$', views.front, name="front"),
              url(r'^accounts/login/$', login, name="login"),
              url(r'^accounts/logout/$', logout, name="logout"),
              #(r'^''accounts/register/$', views.register),
              url(r'^static/$', views.no_view, name='static_url'),
              url(r'^jsrecord/', include('jsrecord.urls')),
              url(r'^entrez/', include('entrezutils.urls')),
              #url(r'^search/', include('haystack.urls')),
              #(r'^static/(?P<path>.*)$', 
              # 'django.views.static.serve',
              # {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
)

#add the generics
generic_views_list = views.generic_forms_list + ['paper', 'dataset', 'sample']

for v in generic_views_list:
    urlpatterns += patterns('',
                           url(r'^new_%s_form/$' % v,
                               getattr(views, "new_%s_form" % v),
                               name="new_%s_form" % v),)

#add generic update
for v in views.generic_update_list:
    urlpatterns += patterns('',
                            url(r'^update_%s_form/(\d+)/$' % v,
                                getattr(views, "update_%s_form" % v),
                                name="update_%s_form" % v),)

#add generic model views
for v in views.generic_model_list:
    view_name = "%s" % v.lower()
    urlpatterns += patterns('', url(r'%s'%view_name, getattr(views, view_name),
                                    name=view_name),)
urlpatterns += patterns('', url(r'assemblies', views.assemblies, 
                                name="assemblies"),)

if settings.DEBUG:
    urlpatterns += patterns('',
    # Uncomment on non-production servers, if you want to debug with 
    # "runserver": For static files during DEBUG mode:
              (r'^static/(?P<path>.*)$', 
               'django.views.static.serve',
               {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
)
