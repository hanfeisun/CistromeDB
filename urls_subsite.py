from django.conf.urls.defaults import *
from datacollection import views
from django.contrib.auth.views import login, logout
import settings

urlpatterns = patterns('',
              url(r'^$', views.papers, name="home"),
              url(r'^new_paper_form/$', views.new_paper_form, 
                  name="new_paper_form"),
              url(r'^new_dataset_form/$', views.new_dataset_form,
                  name="new_dataset_form"),
              url(r'^all_papers/$', views.all_papers, name="all_papers"),
              url(r'^get_datasets/(\d+)/$', views.get_datasets, 
                  name="get_datasets"),
              url(r'^datasets/$', views.datasets, name="datasets"),
              url(r'^accounts/login/$', login, name="login"),
              url(r'^accounts/logout/$', logout, name="logout"),
              #(r'^''accounts/register/$', views.register),
              url(r'^static/$', views.no_view, name='static_url'),
              #(r'^static/(?P<path>.*)$', 
              # 'django.views.static.serve',
              # {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
)

if settings.DEBUG:
    urlpatterns += patterns('',
    # Uncomment on non-production servers, if you want to debug with 
    # "runserver": For static files during DEBUG mode:
              (r'^static/(?P<path>.*)$', 
               'django.views.static.serve',
               {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
)
