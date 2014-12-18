# from haystack.indexes import *
# from haystack import site
# from models import paper__references, Samples
#
#
# class paper__referencesIndex(SearchIndex):
#     #NOTE: text is here by convention; this is where everything is aggregated
#     #define a template to pull out the relevant search fields
#     text = CharField(document=True, use_template=True)
#
#
#
#
# site.register(paper__references, paper__referencesIndex)
# site.register(Samples, SamplesIndex)

from haystack import indexes
from models import Datasets

class DatasetIndex(indexes.SearchIndex, indexes.Indexable):
    id = indexes.CharField(model_attr='id')
    text = indexes.CharField(document=True, use_template=True)
    paper__reference = indexes.CharField()
    factor__name = indexes.CharField(faceted=True)
    cell_line__name = indexes.CharField(faceted=True)
    cell_type__name = indexes.CharField(faceted=True)
    cell_pop__name = indexes.CharField(faceted=True)
    strain__name = indexes.CharField(faceted=True)
    disease_state__name = indexes.CharField(faceted=True)
    species__name = indexes.CharField(faceted=True)
    def prepare(self, object):
        self.prepared_data = super(DatasetIndex, self).prepare(object)
        self.prepared_data['paper__reference'] = object.paper.reference if object.paper else ""
        self.prepared_data['factor__name'] = object.factor.name if object.factor else ""
        self.prepared_data['cell_line__name'] = object.cell_line.name if object.cell_line else ""
        self.prepared_data['cell_type__name'] = object.cell_type.name if object.cell_type else ""
        self.prepared_data['cell_pop__name'] = object.cell_pop.name if object.cell_pop else ""
        self.prepared_data['strain__name'] = object.strain.name if object.strain else ""
        self.prepared_data['disease_state__name'] = object.disease_state.name if object.disease_state else ""
        self.prepared_data['species__name'] = object.species.name if object.species else ""
        return self.prepared_data

    def get_model(self):
            return Datasets

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(factor__name__isnull=False).exclude(status="new")
# class SampleIndex(indexes.SearchIndex, indexes.Indexable):
#     id = indexes.CharField(model_attr='id')
#     text = indexes.CharField(document=True, use_template=True)
#
#
#     def get_model(self):
#         return Samples
#
#     def index_queryset(self, using=None):
#         return self.get_model().objects.filter(factor__name__isnull=False).exclude(status="new")
