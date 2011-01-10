from django.conf.urls.defaults import *
from datacollection import views
from django.contrib.auth.views import login, logout
import settings

urlpatterns = patterns('',
              url(r'^$', views.papers, name="home"),
              #SEE how we reduce the redundancy below
              #url(r'^new_paper_form/$', views.new_paper_form, 
              #    name="new_paper_form"),
              url(r'^all_papers/$', views.all_papers, name="all_papers"),
              url(r'^get_datasets/(\d+)/$', views.get_datasets, 
                  name="get_datasets"),
              url(r'^paper_submission/$', views.paper_submission,
                  name="paper_submission"),
              url('^submissions_admin/$', views.submissions_admin,
                  name="submissions_admin"),
              url(r'^datasets/$', views.datasets, name="datasets"),
              url(r'^accounts/login/$', login, name="login"),
              url(r'^accounts/logout/$', logout, name="logout"),
              #(r'^''accounts/register/$', views.register),
              url(r'^static/$', views.no_view, name='static_url'),
              url(r'^jsrecord/', include('jsrecord.urls')),
              #(r'^static/(?P<path>.*)$', 
              # 'django.views.static.serve',
              # {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
)

#add the generics
generic_views_list = ['paper', 'dataset',
                      'platform','factor','celltype','cellline', 'cellpop',
                      'strain', 'condition', 'journal']

for v in generic_views_list:
    urlpatterns += patterns('',
                           url(r'^new_%s_form/$' % v,
                               getattr(views, "new_%s_form" % v),
                               name="new_%s_form" % v),)
    

if settings.DEBUG:
    urlpatterns += patterns('',
    # Uncomment on non-production servers, if you want to debug with 
    # "runserver": For static files during DEBUG mode:
              (r'^static/(?P<path>.*)$', 
               'django.views.static.serve',
               {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
)
