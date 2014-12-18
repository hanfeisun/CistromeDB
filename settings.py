# Django settings for newdc project.

#LEN-DEFINED values
#where newdc is deployed
DEPLOY_DIR="/data/newdc1.4/src/"
# STATIC_ROOT=
STATIC_URL="/dc_statics/"
STATICFILES_DIRS=("/data/newdc1.4/src/dc_statics",)
#DEFINES sub-site prefix
SUB_SITE=""

from settings_common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

#OBSOLETE:
# DATABASE_ENGINE = 'mysql'
# DATABASE_NAME = 'newdc'
# DATABASE_USER = 'newdc'
# DATABASE_PASSWORD = 'helamcf7'
# DATABASE_HOST = ''
# DATABASE_PORT = ''

DATABASES = {
   'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'newdc2',
        'USER': 'hanfei',
        'PASSWORD': 'cptbtptp',
        'HOST': '',
        'PORT': '',
        'OPTIONS': { 'init_command': 'SET storage_engine=InnoDB;' },
        'STORAGE_ENGINE': 'INNODB'

    },
    'cistromeap':{
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cistromeap',
        'USER': 'hanfei',
        'PASSWORD': 'cptbtptp',

}

}

LOGIN_URL='/dc/accounts/login/'
LOGIN_REDIRECT_URL='/dc/main'
