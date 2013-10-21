# Django settings for newdc project.                                                                                    
                                                                                                                        
#LEN-DEFINED values                                                                                                     
#where newdc is deployed                                                                                                
DEPLOY_DIR="/Users/wuwuqiu/Desktop/Projects/cistrome/database/src"
STATIC_ROOT="/data1/newdc1.4/src/dc_statics"                                                                            
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
        'NAME': 'newdc',                                                                                                
        'USER': 'root',                                                                                                
        'PASSWORD': '',                                                                                         
        'HOST': '',                                                                                                     
        'PORT': '',
        'OPTIONS': { 'init_command': 'SET storage_engine=MyISAM;' }
    },
   
}                                                                                                                       
                                                                                                                        
LOGIN_URL='/dc/accounts/login/'                                                                                         
LOGIN_REDIRECT_URL='/dc/'  
