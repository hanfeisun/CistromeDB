#import datetime
#from haystack.indexes import *
from haystack import indexes
from haystack import site
from datacollection.models import Factors
from datacollection import models
#from models import Factors


class GenericIndex(indexes.SearchIndex):
    #NOTE: text is here by convention; this is where everything is aggregated
    #define a template to pull out the relevant search fields
    text = indexes.CharField(document=True, use_template=True, template_name=['search/indexes/swami/generic_text.txt'])

    # We add this for autocomplete.
    content_auto = indexes.EdgeNgramField(model_attr='name')

#site.register(Factors, FactorsIndex)


_models = ['Factors', 'Species', 'CellLines', 'CellTypes', 'CellPops', 
           'TissueTypes', 'Strains', 'DiseaseStates']

for m in _models:
    model = getattr(models, m)
    site.register(model, GenericIndex)
