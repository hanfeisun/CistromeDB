import glob
import json
from datacollection import models
jfiles = glob.glob("/data1/DC_results/codes/one_json/json/*.json")
for i in jfiles:
    datasetid = int(i.split("/")[-1].split(".")[0])

    with open(i,"r") as a_jfile:
        json_data = json.load(a_jfile)[str(datasetid)]
    # qc = models.Qc(fastqc="P" if json_data["fastqc"] else "F",
    #                mapped="P" if json_data["mapped"] else "F",
    #                map_ratio="P" if json_data["map_ratio"] else "F",
    #                pbc="P" if json_data["pbc"] else "F",
    #                peaks="P" if json_data["peaks"] else "F",
    #                frip="P" if json_data["frip"] else "F",
    #                dhs ="P" if json_data["dhs"] else "F",
    #                motif="P" if json_data["motif"] else "F")
    # qc.save()
    try:
        ds = models.Datasets.objects.get(id=datasetid)
    except:
        print datasetid
        continue
    qc = "".join(["P" if json_data["fastqc"] else "F",
          "P" if json_data["mapped"] else "F",
          "P" if json_data["map_ratio"] else "F",
          "P" if json_data["pbc"] else "F",
          "P" if json_data["peaks"] else "F",
          "P" if json_data["frip"] else "F",
          "P" if json_data["dhs"] else "F",
          "P" if json_data["motif"] else "F"])
    ds.qc_summary = qc
    ds.save()
