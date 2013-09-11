__author__ = 'Hanfei Sun'

from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    url(r'GetGSMInfo/', GetGSMInfo),
)

