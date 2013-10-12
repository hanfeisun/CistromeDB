from django.contrib import admin
from models import *
from django.utils.translation import ugettext_lazy as _
import re


# from datacollection.widgets import *

from django.contrib.admin import site
import adminactions.actions as actions

# register all adminactions
actions.add_to_site(site)

class ImpactFactorFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('impact factor')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'impact'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('>5', _('larger than 5')),
            ('>10', _('larger than 10')),
            )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == '>5':
            return queryset.filter(paper__journal__impact_factor__gt=5)
        if self.value() == '>10':
            return queryset.filter(paper__journal__impact_factor__gt=10)


class DatasetInline(admin.TabularInline):
    model = Datasets
    fields = ['user', 'paper', 'treats', 'conts', 'status']
    raw_id_fields = ['treats', 'conts']


class PaperAdmin(admin.ModelAdmin):
    list_display = ['pmid', 'title', 'journal', 'date_collected', 'pub_date', 'status']
    list_filter = ['journal', 'date_collected', 'pub_date', 'status']
    search_fields = ['title', '@abstract', 'journal']
    list_per_page = 50
    inlines = [DatasetInline, ]

    def suit_row_attributes(self, obj):
        css_class = {
            'complete': 'success',
            'error': 'error',
            'transfer': 'info',
            'datasets': 'warning',
            'imported': 'warning'
        }.get(obj.status)
        if css_class:
            return {'class': css_class}


class DatasetAdmin(admin.ModelAdmin):
    fields = ['user', 'paper', 'treats', 'conts', 'date_created', 'status', 'comments']
    raw_id_fields = ['treats', 'conts']
    list_display = ['id', 'paper', 'status', 'journal_name', 'journal_impact_factor', 'factor', 'treat_ids',
                    'control_ids']
    list_filter = ['status', 'paper__journal', 'treats__factor__name', 'treats__factor__type', ImpactFactorFilter]
    search_fields = ['paper__title', 'paper__pmid', 'paper__journal__name', 'treats__factor__name']
    list_per_page = 100

#    def suit_row_attributes(self, obj):
#        css_class = {
#            1: 'success',
#            0: 'warning',
#            -1: 'error',
#            }.get(obj.status)
#        if css_class:
#            return {'class': css_class, 'data': obj.name}

class SampleAdmin(admin.ModelAdmin):
    list_display = ['unique_id_url','other_id','custom_name', 'factor', 'species', 'cell_category', 'cell_source', 'condition',
                    'custom_antibody','custom_description','action']
    search_fields = ['id', 'unique_id','other_ids', 'factor__name', 'species__name', 'cell_type__name', 'cell_line__name',
                     'cell_pop__name', 'strain__name', 'name',
                     'condition__name',
                     'disease_state__name', 'tissue_type__name', 'antibody__name','description']
    list_display_links = ['action']
    list_filter = ['species__name','factor__name', 'factor__type','status']
    list_per_page = 50
    related_search_fields = {
        'factor': ('name',),
        'cell_type': ('name',),
        'cell_pop': ('name',),
        'cell_line': ('name',),
        'condition': ('name',),
        'strain': ('name',),
        'disease_state': ('name',),
        'tissue_type': ('name',),
        'antibody': ('name',),
    }
#    massadmin_exclude = ['name','unique_id','description','user','other_ids']

    def suit_row_attributes(self, obj, request):
        css_class = {
            'imported': 'success',
            'new': 'warning',
            }.get(obj.status)
        if css_class:
            return {'class': css_class}

    def custom_name(self,obj):
        return obj.name.replace("_"," ")
    def unique_id_url(self,obj):

        return '<a href="http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=%s" target="_blank">%s</a>' % (obj.unique_id, obj.unique_id)

        return ret
    def other_id(self,obj):
        ret = ""
        try:
            other_ids = json.loads(obj.other_ids)
        except:
            return ret
        if other_ids['pmid']:
            pmid = other_ids['pmid'].strip()
            ret += '<a href="http://www.ncbi.nlm.nih.gov/pubmed/%s" target="_blank">P%s</a><br>' %(pmid, pmid)
        if other_ids['gse'] is not None:
            gse = other_ids['gse'].strip()[-5:]
            ret += '<br><a href="http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE%s" target="_blank">GSE%s</a>' %(gse, gse)
        return ret
    def action(self,obj):
        return "Change"

    def custom_antibody(self,obj):
        if obj.antibody:
            return  re.sub(r'(?i)ANTI[^a-zA-Z0-9_]*(.*)',r'<strong>ANTI</strong> \1',obj.antibody.name)
        else:
            return ""

    def custom_description(self,obj):
        ret = ""
        if obj.description:
            desc_dict = json.loads(obj.description)
            for k in desc_dict:
                ret += "<strong>%s</strong>: %s<br>" %(k.title(), desc_dict[k])
        return ret

    def cell_source(self,obj):
        ret = ""
        if obj.cell_line:
            ret += "<strong>Cell Line</strong>: %s<br>"%obj.cell_line
        if obj.cell_pop:
            ret += "<strong>Cell Pop</strong>: %s<br>"%obj.cell_pop
        if obj.strain:
            ret += "<strong>Strain</strong>: %s<br>"%obj.strain
        return ret

    def cell_category(self,obj):
        ret = ""
        if obj.cell_type:
            ret += "<strong>Cell Type</strong>: %s<br>"%obj.cell_type

        if obj.disease_state:
            ret += "<strong>Disease</strong>: %s<br>"%obj.disease_state

        if obj.tissue_type:
            ret += "<strong>Tissue</strong>: %s<br>"%obj.tissue_type

        return ret
    custom_antibody.allow_tags = True
    custom_antibody.short_description = 'Antibody'
    custom_antibody.admin_order_field = 'antibody'
    custom_description.allow_tags = True
    custom_description.short_description = "Description"
    custom_name.short_description = "Name"
    custom_name.admin_order_field = 'name'
    cell_source.allow_tags = True
    cell_category.allow_tags = True

    unique_id_url.short_description = 'Sample ID'
    unique_id_url.allow_tags = True
    unique_id_url.admin_order_field = 'unique_id'
    other_id.short_description = 'Other ID'
    other_id.allow_tags = True

    ordering = ['-id']

class JournalAdmin(admin.ModelAdmin):
    list_display = ['name', 'issn', 'impact_factor']
    list_per_page = 100

class FactorAdmin(admin.ModelAdmin):
    list_display = ['id','type','name','status']
    search_fields = ['id','name']

class CelllineAdmin(admin.ModelAdmin):
    list_display = ['id','name']
    search_fields = ['id','name']

class CelltypeAdmin(admin.ModelAdmin):
     list_display = ['id','name']
     search_fields = ['id','name']
class CellpopAdmin(admin.ModelAdmin):
     list_display = ['id','name']
     search_fields = ['id','name']
class DiseaseAdmin(admin.ModelAdmin):
     list_display = ['id','name']
     search_fields = ['id','name']
class StrainAdmin(admin.ModelAdmin):
     list_display = ['id','name']
     search_fields = ['id','name']
class AntibodyAdmin(admin.ModelAdmin):
     list_display = ['id','name']
     search_fields = ['id','name']
class ConditionAdmin(admin.ModelAdmin):
     list_display = ['id','name']
     search_fields = ['id','name']
admin.site.register(Papers, PaperAdmin)
admin.site.register(Samples, SampleAdmin)
admin.site.register(Datasets, DatasetAdmin)
admin.site.register(Journals, JournalAdmin)
admin.site.register(Factors,FactorAdmin)
admin.site.register(CellTypes, CelltypeAdmin)
admin.site.register(CellLines, CelllineAdmin)
admin.site.register(CellPops,CellpopAdmin)
admin.site.register(DiseaseStates,DiseaseAdmin)
admin.site.register(Strains, StrainAdmin)
admin.site.register(Antibodies,AntibodyAdmin)
admin.site.register(Conditions, ConditionAdmin)
