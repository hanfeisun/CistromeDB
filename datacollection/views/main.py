import glob
import json as json
import os
import subprocess
from itertools import chain


from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page
from datacollection.models import Datasets



ab_cellline = "cl"
ab_celltype = "ct"
ab_cellpop = "cp"
ab_strain = "st"


def main_view_ng(request):
    if not request.is_ajax():
        return render_to_response('datacollection/DC_browser_main_ng.html',
                                  context_instance=RequestContext(request))


@cache_page(60 * 60 * 24)

def main_filter_ng(request):
    req_s = request.GET.get("species", None)
    req_c = request.GET.get("cellinfos", None)
    req_f = request.GET.get("factors", None)
    req_p = int(request.GET.get("page", 1))
    req_hide_incomplete = request.GET.get("hideincomplete", "false")
    req_hide_unvalidated = request.GET.get("hideunvalidated", "true")
    req_keyword = request.GET.get("keyword", "")


    clicked = request.GET.get("clicked", None)
    # q_common = (Q(status="checked") | Q(status="inherited") | Q(status="running") | Q(status="complete")) & Q(
    #     factor__status="ok") & Q(TREATS__isnull=False)

    # q_common = Q(TREATS__status="complete") | Q(TREATS__status="valid")

    if req_hide_incomplete == "true":
        # Show processsed datasets
        q_common = Q(status="complete")

    else:
        if req_hide_unvalidated == "false":
            # Show all datasets
            q_common = Q()
        else:
            # Show validated datasets
            q_common = Q(status="complete") | Q(status="validated")

    if request.is_ajax() and (not (req_s and req_c and req_f)):
        return HttpResponse("Request denied!")

    if req_s == "all" or req_s == None:
        q_s = Q()
    else:
        q_s = Q(species__name=req_s)

    if req_f == "all" or req_f == None:
        q_f = Q()
    elif req_f == "None":
        q_f = Q(factor__isnull=True)
    else:
        q_f = Q(factor__name=req_f)

    if req_c == "all" or req_c == None:
        q_c = Q()
    else:
        clip = lambda x: x[3:]
        if req_c.startswith(ab_cellline):
            q_c = Q(cell_line__name=clip(req_c))
        elif req_c.startswith(ab_cellpop):
            q_c = Q(cell_pop__name=clip(req_c))
        elif req_c.startswith(ab_celltype):
            q_c = Q(cell_type__name=clip(req_c))
        elif req_c.startswith(ab_strain):
            q_c = Q(strain__name=clip(req_c))

    datasets = Datasets.objects.filter(q_s & q_f & q_c & q_common)



    if req_keyword:

        datasets = datasets.filter(full_text__iregex="[[:<:]]" + req_keyword)


        # original_key = "".join(map(str, [req_s, req_c, req_f, req_keyword]))
        # key = hashlib.sha256(original_key).hexdigest()
        # if cache.get(key):
        #     datasets = cache.get(key)
        # else:
        #     datasets = datasets.filter(full_text__iregex="[[:<:]]" + req_keyword)
        #
        #     _timeout = 60 * 60 # 1 hour
        #     cache.set(key, datasets, _timeout)

    species = datasets.values_list("species__name", flat=True).order_by("species__name").distinct()
    if clicked != "factor_filter":
        factors = datasets.values_list("factor__name", flat=True).order_by("factor__name").distinct()
    else:
        factors = []

    if clicked != "cell_filter":
        celllines = [(ab_cellline, i) for i in
                     datasets.filter(cell_line__status="ok").values_list("cell_line__name", flat=True).distinct()]
        celltypes = [(ab_celltype, i) for i in
                     datasets.filter(cell_type__status="ok").values_list("cell_type__name", flat=True).distinct()]
        cellpops = [(ab_cellpop, i) for i in
                    datasets.filter(cell_pop__status="ok").values_list("cell_pop__name", flat=True).distinct()]
        strains = [(ab_strain, i) for i in
                   datasets.filter(strain__status="ok").values_list("strain__name", flat=True).distinct()]

        cellinfos = sorted(chain(celllines, celltypes, cellpops, strains), key=lambda s: s[1].lower())

    else:
        cellinfos = []

    # samples_ids = datasets.values("TREATS__id").annotate(t=Max("TREATS__id"), id=Max("id")).order_by("t")
    datasets_paginator = Paginator(datasets, 20)
    datasets_in_current_page = datasets_paginator.page(req_p)

    datasets_current = datasets_in_current_page.object_list.values("species__name", "factor__name",
                                                                   "cell_line__name", "cell_pop__name",
                                                                   "cell_type__name", "strain__name",
                                                                   "tissue_type__name",
                                                                   "paper__reference",
                                                                   "status",
                                                                   "paper__pub_summary",
                                                                   "id")


    return HttpResponse(
        json.dumps({"species": list(species), "factors": list(factors), "cellinfos": list(cellinfos),
                    "datasets": list(datasets_current), "num_pages": datasets_paginator.num_pages, "request_page": req_p}),
        mimetype='application/json')





@cache_page(60 * 60 * 24)
def inspector_ajax(request):
    """ inspector views 
    """
    req_dataset_id = request.GET.get("id", None)
    if not req_dataset_id:
        return HttpResponse("Request denied!")
    else:
        dataset = Datasets.objects.get(id=req_dataset_id)
        status = dataset.status
        treats = dataset.treats.all().values("species__name", "factor__name",
                                             "cell_line__name", "cell_pop__name",
                                             "cell_type__name", "strain__name",
                                             "tissue_type__name",
                                             "paper__journal__name", "disease_state__name",
                                             "paper__reference", "paper__lab", "paper__pmid",
                                             "name", "other_ids", "unique_id").order_by("name")
        
        conts = dataset.conts.all().values("unique_id", "name").order_by("name")
        # Quality report and tooltip part, send json to Angular
        try:
            json_f = open("/data1/DC_results/codes/one_json/json/%s.json" % req_dataset_id, "r")
            json_data = json.load(json_f)
            json_f.close()
        except IOError:
            json_data = {}
        return HttpResponse(
            json.dumps({"id": req_dataset_id, "treats": list(treats), "conts": list(conts), "qc": json_data,  "status": status}),
            mimetype='application/json')

@cache_page(60 * 60 * 24)
def show_image(request):
    req_id = request.GET.get("id", None)

    if not (req_id):
        return HttpResponse("Wrong parameter")
    try:
        req_id = str(req_id)
    except:
        return HttpResponse("id not available")
    conserv_dir = "/data/home/qqin/Workspace/Active/NewSpeciesConservation/ConservFigs"
    try:
        img = glob.glob(os.path.join(conserv_dir, req_id+"_*"+".png"))[0]
        with open(img, "rb") as f:
            return HttpResponse(f.read(), mimetype = "image/png")
    except IndexError:
        err = {req_id: "not found image"}
        return HttpResponse(json.dumps(err), mimetype='application/json')

@cache_page(60 * 60 * 24)
def similarity_ajax(request):
    req_dataset_id = request.GET.get("id",None)
    if not req_dataset_id:
        return HttpResponse("Request denied")
    else:
        try:
            json_f = open("/data/home/hanfei/dc_intersect_result/%s_intersect.json" % req_dataset_id)
            json_orig = json.load(json_f)
            json_sorted = sorted(json_orig,key=lambda x:x[1],reverse=True)[:20]
            ids = [int(js[0]) for js in json_sorted]
            datasets = Datasets.objects.filter(id__in=ids).values("factor__name",
                                                                             "cell_line__name", "cell_pop__name",
                                                                             "cell_type__name", "strain__name",
                                                                             "tissue_type__name")
            json_result = [[ds, js[1]] for js,ds in zip(json_sorted, datasets)]

            json_f.close()
        except IOError:
            json_result = {}
        return HttpResponse(json.dumps(json_result), mimetype="application/json")
