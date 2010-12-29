from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
                           (r'load/(\w+)/', loader),
                           (r'(\w+)/(\w+)/(\d+)?/?$', router),
                           )
