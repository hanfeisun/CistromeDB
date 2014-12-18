import os
from glob import glob
from datacollection import models

prefix = ["/data3/DC/DC_results/HgChIPseq","/data3/DC/DC_results/MmChIPseq", "/data3/DC/DC_results/HgDNase"]
for a_dataset in models.Datasets.objects.all():
    id = str(a_dataset.id)
    for a_prefix in prefix:
        folder = a_prefix +"/dataset%s"%id
        if os.path.exists(folder):
            summit_match = glob(folder + "/*summits.bed")
            if summit_match:
                a_dataset.summit_file = summit_match[0]
                print a_dataset.summit_file
                a_dataset.save()

            summary_match = glob(folder + "/*summary.txt")
            if summary_match:
                a_dataset.summary_file = summary_match[0]
                print a_dataset.summary_file
                a_dataset.save()

            bw_match = glob(folder + "/*treat*.bw")
            if bw_match:
                a_dataset.treat_bw_file = bw_match[0]
                print a_dataset.treat_bw_file
                a_dataset.save()


            con_match = glob(folder + "/*conserv.png")
            if con_match:
                a_dataset.conservation_file = con_match[0]
                print a_dataset.conservation_file
                a_dataset.save()

            ceas_match = glob(folder + "/*ceas*.pdf")
            if ceas_match:
                a_dataset.ceas_file = ceas_match[0]
                print a_dataset.ceas_file
                a_dataset.save()





