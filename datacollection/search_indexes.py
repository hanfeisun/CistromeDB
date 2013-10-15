#import datetime
from haystack.indexes import *
from haystack import site
from models import Papers, Samples


class PapersIndex(SearchIndex):
    #NOTE: text is here by convention; this is where everything is aggregated
    #define a template to pull out the relevant search fields
    text = CharField(document=True, use_template=True)    

class SamplesIndex(SearchIndex):
    text = CharField(document=True, use_template=True)    

site.register(Papers, PapersIndex)
site.register(Samples, SamplesIndex)
