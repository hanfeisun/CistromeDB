import glob
import json as json
import os
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from datacollection.models import Datasets
import subprocess
import re

from django.shortcuts import redirect

__author__ = 'hanfei'

@cache_page(60 * 60 * 24)
def motif_json(request):
    req_id = request.GET.get("id", None)
    req_gene = request.GET.get("id", None)
    if not (req_id):
        return HttpResponse("Wrong Parameter")

    qc_motif = "/data/home/qqin/Workspace/Achieved/DCjsons/motif_json/"+str(req_id)+".json"

    if not os.path.exists(qc_motif):
        return HttpResponse("Wrong Parameter")

    inf = open(qc_motif)
    content = json.load(inf)
    return HttpResponse(json.dumps(content, indent=4), content_type="application/json")

@cache_page(60 * 60 * 24)
def target_json(request):
    req_id = request.GET.get("id", None)
    req_gene = request.GET.get("gene", None)
    if not (req_id):
        return HttpResponse("Wrong parameter")

    folder = Datasets.objects.get(id=int(req_id)).result_folder
    if not folder:
        return HttpResponse("Dataset not processed")
    matches = glob.glob(folder + "/attic/*gene_score.txt")
    if not matches:
        return HttpResponse("File Not found")
    target_file = matches[0]
    target_cnt = 0
    gene_dict = {}
    target_list = []
    gene_scanned = []
    with open(target_file) as tf:
        for line in tf:
            if line.startswith("#"):
                continue
            if target_cnt == 100:
                break
            cols = line.strip().split("\t")

            gene_symbol = cols[6]
            if req_gene and cols[6].upper() != req_gene.upper():
                continue

            visual_coordinate = cols[0] + ":" + str(max(int(cols[1])-100000, 0)) + "-" + str(int(cols[2]) + 100000)
            if req_gene:
                target_list = [
                    {"coordinate":cols[0]+ ":" + cols[1] +"-" + cols[2], "score": cols[4], "symbol": gene_symbol,
                     "visual_coordinate": visual_coordinate}]
                break
            if gene_symbol in gene_scanned:
                continue
            else:
                gene_scanned.append(gene_symbol)

            if gene_dict.has_key(visual_coordinate):
                if gene_symbol not in gene_dict[visual_coordinate]["symbol"]:
                    target_list[gene_dict[visual_coordinate]["location"]]["symbol"] += " / %s" % gene_symbol

            else:
                gene_dict[visual_coordinate] = {"location": target_cnt, "symbol": [gene_symbol]}


            if float(cols[4]) <= 0:
                break

            target_list += [
                {"coordinate":cols[0] + ":" + cols[1] + "-" + cols[2], "score": cols[4], "symbol": cols[6],
                 "visual_coordinate": visual_coordinate}]

            target_cnt += 1

    return HttpResponse(json.dumps(target_list))


def file_view(request):
    req_type = request.GET.get("type", None)
    req_id = request.GET.get("id", None)
    if not (req_id and req_type):
        return HttpResponse("Wrong parameter")

    folder = Datasets.objects.get(id=int(req_id)).result_folder
    if not folder:
        return HttpResponse("Dataset not processed")

    if req_type == "bed":
        matches = glob.glob(folder + "/*.narrowPeak.gz")  # change to shorter peak names

        if matches:
            target_file = matches[0]
            return redirect("http://cistrome.org/"+target_file)


    elif req_type == "bw":
        matches = glob.glob(folder + "/*treat*.bw")
        if not matches:
            return HttpResponse("File Not found")
        target_file = matches[0]
        return redirect("http://cistrome.org" + target_file)


        # if not request.user.is_authenticated() and not request.META["REMOTE_ADDR"] == "127.0.0.1":
        #     return HttpResponse("Downloading needs login first.")
        # response = HttpResponse(open(target_file, "r"), mimetype='text/octet-stream')
        # response['Content-Disposition'] = "attachment; filename=%s.bw" % req_id
        # response['Content-Length'] = os.stat(target_file).st_size
        # return response


    elif req_type == "pt":
        matches = glob.glob(folder + "/attic/*gene_score.txt")
        if matches:
            target_file = matches[0]
            return redirect("http://cistrome.org/"+target_file)
    return HttpResponse(status=404)
import urllib
def hgtext_view(request, dataset_id=None):
    dataset =  Datasets.objects.get(id=int(dataset_id))
    folder = dataset.result_folder

    db = request.GET.get("db", None)
    position = request.GET.get("position", None)

    bw_matches = [i for i in glob.glob(folder + "/*treat*.bw") if "_rep" not in i]
    bb_matches = [i for i in glob.glob(folder + "/*.narrowPeak.bb") if "_rep" not in i]

    if bw_matches and bb_matches and db:

        bw_m = bw_matches[0]
        bb_m = bb_matches[0]
        bw_name = bw_m.split("/")[-1]
        bb_name = bb_m.split("/")[-1]
        anno_text = '''
track type=bigBed bigDataUrl=http://cistrome.org{bb_m} name="{bb_name}"
track type=bigWig bigDataUrl=http://cistrome.org{bw_m} name="{bw_name}" visibility=2'''.format(**locals())

        result_url = "http://genome.ucsc.edu/cgi-bin/hgTracks?db=" + db + "&hgct_customText="+urllib.quote_plus(anno_text)
        if position:
            result_url += "&position=" + position
        return redirect(result_url)
    elif not bw_matches:
        return HttpResponse("Can't find BIGWIG file")
    else:
        return HttpResponse("Can't find BIGBED file")
def datahub_view(request, dataset_id=None):
    folder = Datasets.objects.get(id=int(dataset_id)).result_folder

    bw_matches = [i for i in glob.glob(folder + "/*treat*.bw") if "_rep" not in i]
    bed_matches = [i for i in glob.glob(folder + "/*.narrowPeak.gz") if "_rep" not in i]
    if bw_matches and bed_matches:
        bw_target = bw_matches[0]
        bed_target = bed_matches[0]
        return \
            HttpResponse(json.dumps(
                [{"type": "bigwig", "url": "http://cistrome.org" + bw_target, "mode": "show", "height": 50, "name": bw_target.split("/")[-1]},
                 {"type": "bed", "url": "http://cistrome.org" + bed_target, "mode": "show", "height": 50, "name": bed_target.split("/")[-1]}]),
                         mimetype='application/json')
    elif not bw_matches:
        return HttpResponse("Can't find BIGWIG file")
    else:
        return HttpResponse("Can't find BED file")
