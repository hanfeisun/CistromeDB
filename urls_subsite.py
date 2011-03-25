from django.conf.urls.defaults import *
from datacollection import views
from django.contrib.auth.views import login, logout
import settings

urlpatterns = patterns('',
              url(r'^$', views.papers, name="home"),
              #SEE how we reduce the redundancy below
              #url(r'^new_paper_form/$', views.new_paper_form, 
              #    name="new_paper_form"),
              url(r'^all_papers/(\d+/)?$', views.all_papers,name="all_papers"),
              url(r'^weekly_papers/(\d+)/$',
                  views.weekly_papers, name="weekly_papers"),
              url(r'^datasets/(\d+/)?$', views.datasets, name="datasets"),
              url(r'^weekly_datasets/(\d+)/$',
                  views.weekly_datasets, name="weekly_datasets"),
              url(r'^admin/$', views.admin, name="admin"),
              url(r'^report/$', views.report, name="report"),
              url(r'^teams/$', views.teams, name="teams"),
              url(r'^paper_profile/(\d+)/$', views.paper_profile,
                  name="paper_profile"),
              url(r'^dataset_profile/(\d+)/$', views.dataset_profile,
                  name="dataset_profile"),
              url(r'^replicate_profile/(\d+)/$', views.replicate_profile,
                  name="replicate_profile"),
              url(r'^get_datasets/(\d+)/$', views.get_datasets, 
                  name="get_datasets"),
              url(r'^paper_submission/$', views.paper_submission,
                  name="paper_submission"),
              url('^submissions_admin/$', views.submissions_admin,
                  name="submissions_admin"),
              url('^auto_paper_import/$', views.auto_paper_import,
                  name="auto_paper_import"),
              url('^import_datasets/(\d+)/$', views.import_datasets,
                  name="import_datasets"),
              url('^download_datasets/(\d+)/$', views.download_datasets,
                  name="download_datasets"),
              url('^upload_dataset_form/(\d+)/$', views.upload_dataset_form,
                  name="upload_dataset_form"),
              url(r'^datasets/$', views.datasets, name="datasets"),
              url(r'^batch_update_datasets/$', views.batch_update_datasets,
                  name="batch_update_datasets"),
              url(r'^search/$', views.search, name="search"),
              url(r'^accounts/login/$', login, name="login"),
              url(r'^accounts/logout/$', logout, name="logout"),
              #(r'^''accounts/register/$', views.register),
              url(r'^static/$', views.no_view, name='static_url'),
              url(r'^jsrecord/', include('jsrecord.urls')),
              url(r'^entrez/', include('entrezutils.urls')),
              #(r'^static/(?P<path>.*)$', 
              # 'django.views.static.serve',
              # {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
)

#add the generics
generic_views_list = ['paper', 'dataset',
                      'platform','factor','celltype','cellline', 'cellpop',
                      'strain', 'condition', 'journal',
                      'species', 'filetype', 'assembly', 'replicate']

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

if settings.DEBUG:
    urlpatterns += patterns('',
    # Uncomment on non-production servers, if you want to debug with 
    # "runserver": For static files during DEBUG mode:
              (r'^static/(?P<path>.*)$', 
               'django.views.static.serve',
               {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
)
