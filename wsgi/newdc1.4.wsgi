#!/mnt/Storage/home/qinq/dc2/src/venv/bin/python
import sys
import site
import os

# add the site-packages of our virtualenv as a site dir
site.addsitedir('/mnt/Storage/home/qinq/dc2/src/venv/lib/python2.7/site-packages/')
sys.path.append('/mnt/Storage/home/qinq/dc2/src/')


activate_env='/mnt/Storage/home/qinq/dc2/src/venv/bin/activate_this.py'
execfile(activate_env, dict(__file__=activate_env))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
