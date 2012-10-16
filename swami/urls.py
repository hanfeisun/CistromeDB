from django.conf.urls.defaults import *
#from views import *
import views

urlpatterns = patterns('',)

_models = ['Factors', 'Species', 'CellLines', 'CellTypes', 'CellPops', 
           'TissueTypes', 'Strains', 'DiseaseStates']

for m in _models:
    v = getattr(views, m)
    urlpatterns += patterns('', (r'%s/' % m,  v))
