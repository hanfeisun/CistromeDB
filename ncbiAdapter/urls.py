__author__ = 'Hanfei Sun'

from django.conf.urls import patterns, url, include


from views import *

urlpatterns = patterns('',
    url(r'GetGSMInfo/', GetGSMInfo),
)

