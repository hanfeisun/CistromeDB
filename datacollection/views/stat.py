from django.db.models import Q
from django.shortcuts import render_to_response
from datacollection.models import Samples, Papers

__author__ = 'hanfei'


def DC_stat_view(request):
    data = ModelDataSource(Samples.objects.raw(
        "select id,COUNT(ID) as count,status from datacollection_samples group by status order by FIELD(status, 'checked', 'new','ignored','inherited');"),
                           fields=["status", "count"]);
    chart = gchart.PieChart(data, options={'title': "Sample Progress"})
    # chart.__class__.get_series = get_series_pack


    all_samples_cnt = Samples.objects.count()

    has_cell_info_samples = Samples.objects.filter(
        Q(cell_line__isnull=False) | Q(cell_type__isnull=False) | Q(cell_pop__isnull=False) | Q(
            tissue_type__isnull=False))
    has_cell_info_samples_cnt = has_cell_info_samples.count()
    canonical_cell_info_cnt = has_cell_info_samples.filter(
        Q(cell_line__status="ok") | Q(cell_type__status="ok") | Q(cell_pop__status="ok") | Q(
            tissue_type__status="ok")).count()
    data2 = [['Status', 'Count'], ["Samples with validated cell information", canonical_cell_info_cnt],
             ["Samples with no cell information", all_samples_cnt - has_cell_info_samples_cnt],
             ["Samples with unvalidated cell information", has_cell_info_samples_cnt - canonical_cell_info_cnt],

    ]
    chart2 = gchart.PieChart(SimpleDataSource(data=data2), options={"title": "Cell Info Annotation Progress"})

    lack_factor_info_cnt = Samples.objects.filter(factor__name=None).count()
    canonical_factor_info_cnt = Samples.objects.exclude(factor__name=None).exclude(factor__status="new").count()
    data3 = [['Status', 'Count'], ["Samples with canonical factor name", canonical_factor_info_cnt],
             ["Samples with no factor name", lack_factor_info_cnt],
             ["Samples with non-canonical factor name",
              all_samples_cnt - lack_factor_info_cnt - canonical_factor_info_cnt], ]

    chart3 = gchart.PieChart(SimpleDataSource(data=data3), options={"title": "Factor Annotation Progress"})

    orphan_cnt = Samples.objects.filter(TREATS__isnull=True, CONTS__isnull=True).count()
    treat_cnt = Samples.objects.exclude(TREATS__isnull=True).count()
    cont_cnt = Samples.objects.exclude(CONTS__isnull=True).count()
    data4 = [['Status', 'Count'], ["Treat", treat_cnt], ["Orphan", orphan_cnt], ["Control", cont_cnt]]
    chart4 = gchart.PieChart(SimpleDataSource(data=data4), options={"title": "Sample Grouping Progress"})

    data5 = ModelDataSource(Samples.objects.raw(
        "select id,COUNT(id) as count,convert(YEAR(geo_release_date),CHAR(5)) as year from datacollection_samples group by YEAR(geo_release_date);"),
                            fields=["year", "count"])
    chart5 = gchart.ColumnChart(data5, options={"title": "GEO Sample Release Statistics"})

    data6 = ModelDataSource(Papers.objects.raw("select datacollection_journals.id as id, COUNT(datacollection_journals.id) as count, datacollection_journals.name as name from datacollection_journals,datacollection_papers where datacollection_journals.id=datacollection_papers.journal_id group by dataco\
llection_journals.id order by -count(datacollection_journals.id) limit 20"), fields=["name", "count"])
    chart6 = gchart.BarChart(data6, options={"title": "Paper by Jounals"})

    return render_to_response('datacollection/DC_stat_view.html', locals())