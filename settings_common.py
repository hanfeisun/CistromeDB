import os
from settings import DEPLOY_DIR

ADMINS = (('Len Taing', 'lentaing@jimmy.harvard.edu'),
    )

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

#NOTE: this is for django1.2; since daisy only has django1.1, we need to
#comment this out.
# List of callables that know how to import templates from various sources.
# TEMPLATE_LOADERS = (
#     'django.template.loaders.filesystem.Loader',
#     'django.template.loaders.app_directories.Loader',
# #     'django.template.loaders.eggs.Loader',
# )

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = DEPLOY_DIR + 'media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
STATIC_URL = '/dc_statics/'
ADMIN_MEDIA_PREFIX = '/dc_statics/'
# Make this unique, and don't share it with anybody.
SECRET_KEY = '@y7n)31q3q=*0v!kvbg5rq_hhkt$(!#o2u88cr_xshhn=3ij=6'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
    )

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    DEPLOY_DIR + 'templates',
    )

CONF_TEMPLATE_DIR = os.path.join(DEPLOY_DIR, "pipeline", "templates")

MIDDLEWARE_CLASSES = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #    'django.middleware.csrf.CsrfViewMiddleware',


    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    )

ROOT_URLCONF = 'urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'debug_toolbar',
    'haystack',

    # Uncomment the next line to enable the admin:
     'suit',
    'adminactions',
    'django_select2',
    'django.contrib.admin',
    'django.contrib.messages',
    'datacollection', 'jsrecord', 'entrezutils',
       'haystack',
    'south',
    # 'admin_views'
    # 'adminplus',
#    'swami',
    'template_timings_panel'

    )

AUTH_PROFILE_MODULE = 'datacollection.UserProfiles'

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend','datacollection.auths.CistromeAuthBackend')

DEBUG_TOOLBAR_PATCH_SETTINGS = False
#AJAX_SELECT_BOOTSTRAP = True
#AJAX_SELECT_INLINES = 'inline'
#
#AJAX_LOOKUP_CHANNELS = {
#    #   pass a dict with the model and the field to search against
#    'factor'  : {'model':'datacollection.Factors', 'search_field':'name'},
#    'cell_type' : {'model': 'datacollection.CellTypes', 'search_field': 'name'},
#}

#haystack specific
# HAYSTACK_SITECONF = 'search_sites'
# HAYSTACK_SEARCH_ENGINE = '    whoosh'
# HAYSTACK_WHOOSH_PATH = os.path.join(MEDIA_ROOT, 'whoosh_index')



import os
# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
#         'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
#         },
#     }
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
        },
    }
SOUTH_DATABASE_ADAPTERS = {
    'default': "south.db.mysql"
}


# Django-suit specific
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP


TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
    )

SUIT_CONFIG = {
    'ADMIN_NAME': 'DC Admin',
    'MENU': (
        {'app': 'auth', 'label': 'Authorization', 'icon': 'icon-lock'},
        {'app':'datacollection','label':'DataCollection'},
    {'label': 'Widgets', 'icon':'icon-cog', 'url': '/dc/stat/',
     'models': (
        {'label': 'Statistics', 'url': '/dc/stat/'},

    )},
        )
}

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

# GRAPPELLI_AUTOCOMPLETE_SEARCH_FIELDS = {
#     "datacollection": {
#         "factors": ("id__iexact", "name__icontains",)
#     }
# }

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': 'unique-snowflake'
#     }
# }


DATABASE_ROUTERS = ['router.ModelDatabaseRouter']

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': '127.0.0.1:11211',
#         }
# }
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
}



INTERNAL_IPS = ['222.66.175.158','222.66.175.149', '222.66.175.170','222.66.175.130','175.160.5.249','222.66.184.19','222.66.173.165','222.66.189.142','222.66.179.141']
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
    'template_timings_panel.panels.TemplateTimings.TemplateTimings',

    ]

DEBUG = False
TEMPLATE_DEBUG = True
