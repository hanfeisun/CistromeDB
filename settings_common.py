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
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.databrowse',
    # Uncomment the next line to enable the admin:
     'suit',

    'massadmin',
    'adminactions',
    'django.contrib.admin',
    'django.contrib.messages',
    'datacollection', 'jsrecord', 'entrezutils',
    #    'haystack',
    'south',
#    'swami',
    )

AUTH_PROFILE_MODULE = 'datacollection.UserProfiles'

CACHE_BACKEND = 'db://newdc_cache'

#AJAX_SELECT_BOOTSTRAP = True
#AJAX_SELECT_INLINES = 'inline'
#
#AJAX_LOOKUP_CHANNELS = {
#    #   pass a dict with the model and the field to search against
#    'factor'  : {'model':'datacollection.Factors', 'search_field':'name'},
#    'cell_type' : {'model': 'datacollection.CellTypes', 'search_field': 'name'},
#}

#haystack specific
HAYSTACK_SITECONF = 'search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.join(MEDIA_ROOT, 'whoosh_index')

SOUTH_DATABASE_ADAPTERS = {
    'default': "south.db.mysql"
}


# Django-suit specific
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
    )

SUIT_CONFIG = {
    'ADMIN_NAME': 'Cistrome Suit',
    'MENU': (
        {'app': 'auth', 'label': 'Authorization', 'icon': 'icon-lock'},
        {'app':'datacollection','label':'DataCollection'}
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
