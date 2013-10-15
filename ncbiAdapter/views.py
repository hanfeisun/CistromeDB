__author__ = 'Hanfei Sun'

# from geo import createSample
import json
from django.http import HttpResponse

def GetGSMInfo(request):
    GSM_id = request.GET['id']

    # if GSM_id:
    #     tmp = createSample(GSM_id)
    #     tmp_dict = {}
    #     sample_fields = ["name","unique_id"]
    #     pubmed_fields = ["factors","cell_lines","cell_pops","cell_types","tissue_types","authors","abstract","title"]
    #     sample_foreign_fields = ["factor","species","strain","cell_type","disease_state","cell_pop","assembly","antibody","tissue_type"]
    #     pubmed_foreign_fields = ["journal"]

    #     tmp_dict["sample"] = {}
    #     tmp_dict["paper"] = {}
    #     for i in sample_fields:
    #         tmp_dict["sample"][i] = getattr(tmp, i)

    #     for i in sample_foreign_fields:
    #         if getattr(tmp, i):
    #             tmp_dict["sample"][i] = getattr(tmp,i).name
    #         else:
    #             tmp_dict["sample"][i] = "NA"

    #     for i in pubmed_fields:
    #         tmp_dict["paper"][i] = getattr(tmp.paper, i)

    #     for i in pubmed_foreign_fields:
    #         if getattr(tmp.paper, i):
    #             tmp_dict["paper"][i] = getattr(tmp.paper,i).name
    #         else:
    #             tmp_dict["paper"][i] = "NA"
    #     tmp_dict["paper"]["pub_date"] = str(tmp.paper.pub_date)

    #     return HttpResponse(json.dumps(tmp_dict))
    # else:
    return HttpResponse("{'success':false, 'err':'No PMID given!'}")
