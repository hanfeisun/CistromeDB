from django.contrib import admin
from models import *
from django.utils.translation import ugettext_lazy as _

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
    list_display = ['id', 'unique_id', 'factor', 'species', 'cell_type', 'cell_line', 'cell_pop', 'strain', 'condition',
                    'disease_state', 'tissue_type', 'antibody']
    search_fields = ['id', 'unique_id', 'factor__name', 'species__name', 'cell_type__name', 'cell_line__name',
                     'cell_pop__name', 'strain__name',
                     'condition__name',
                     'disease_state__name', 'tissue_type__name', 'antibody__name']
    list_filter = ['factor__name', 'factor__type']
    list_per_page = 50


class JournalAdmin(admin.ModelAdmin):
    list_display = ['name', 'issn', 'impact_factor']
    list_per_page = 100

admin.site.register(Papers, PaperAdmin)
admin.site.register(Samples, SampleAdmin)
admin.site.register(Datasets, DatasetAdmin)
admin.site.register(Journals, JournalAdmin)