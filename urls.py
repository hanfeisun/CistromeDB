# urls.py
from django.conf.urls.defaults import *
import settings


urlpatterns = patterns('',
    (r'^%s' % settings.SUB_SITE, include('urls_subsite')),
)



