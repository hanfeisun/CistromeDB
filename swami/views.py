import sys

# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse
from haystack.query import SearchQuerySet
from datacollection import models

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
        print model_class
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
