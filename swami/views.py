import os
import sys

# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse
from haystack.query import SearchQuerySet
from datacollection import models

from whoosh import index
import settings

#a trick to get the current module
_modname = globals()['__name__']
_this_mod = sys.modules[_modname]

try:
    import json
except ImportError:
    import simplejson as json

# OBSOLETE
# def factors(request):
#     if 'q' in request.GET:
#         res = SearchQuerySet().autocomplete(content_auto=request.GET['q'])
#         tmp = []
#         for r in res:
#             #NOTE: r.model, r.model_name, r.object
#             if r.model == models.Factors:
#                 tmp.append({'id': r.object.id, 'name': r.object.name})

#     return HttpResponse(json.dumps(tmp))

#views factory
def views_factory(model_class):
    def generic_view(request):
        #print model_class
        tmp = []
        if 'q' in request.GET:
            res = SearchQuerySet().autocomplete(content_auto=request.GET['q'])
            for r in res:
                #NOTE: r.model, r.model_name, r.object
                if r.model == model_class:
                    tmp.append({'id': r.object.id, 'name': r.object.name})

        return HttpResponse(json.dumps(tmp))
    return generic_view

#autogenerating views

_models = ['Factors', 'Species', 'CellLines', 'CellTypes', 'CellPops', 
           'TissueTypes', 'Strains', 'DiseaseStates']

for m in _models:
    model = getattr(models, m)
    setattr(_this_mod, m, views_factory(model))

#def update_search_index(request, model, iid):
def update_search_index(request):
    """Tries to update the search index with the current model record
    ref: http://pythonhosted.org/Whoosh/indexing.html#incremental-indexing
    
    NOTE: we do not check for duplicates!
    """
    if 'model' in request.GET and 'id' in request.GET:
        mod = getattr(models, request.GET['model'])
        tmp = mod.objects.get(pk=request.GET['id'])

        if tmp and os.path.exists(settings.HAYSTACK_WHOOSH_PATH):
            ix = index.open_dir(settings.HAYSTACK_WHOOSH_PATH)
            params = {'django_ct':u'datacollection.%s' % mod._meta.module_name,
                      'text':u'%s' % tmp.name,
                      'django_id':u'%s' % tmp.id,
                      'content_auto':u'%s' % tmp.name}
            writer = ix.writer()
            writer.add_document(**params)
            writer.commit()
    #response is always ignored!
    return HttpResponse([])
