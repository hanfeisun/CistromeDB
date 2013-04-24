from django.conf.urls.defaults import *
#from views import *
import views

urlpatterns = patterns('',)

_models = ['Factors', 'Species', 'CellLines', 'CellTypes', 'CellPops', 
           'TissueTypes', 'Strains', 'DiseaseStates']

urlpatterns += patterns('', (r'update_search_index/', 
                             views.update_search_index))
for m in _models:
    v = getattr(views, m)
    urlpatterns += patterns('', (r'%s/' % m,  v))

