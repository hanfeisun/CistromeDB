################# ../bin/python ./scripts/extract_datasets_IF5.py > /data/home/chenfei/shared_users/wuqiu/newdc/files/datasets_info.txt #################################


from django.core.management import setup_environ
import sys
sys.path.insert(0,'/data/newdc1.4/src')
import settings
setup_environ(settings)
from datacollection import models

print "\t".join(["DatasetID","SeriesID","Species","Factor","Cell_type","Cell_line","Tissue_type","Factor_type","Paper","Journal","Impact_factor","Treat","Control","Status"])

for d in models.Datasets.objects.all():
    if not d.treats.all():
        continue
    else:
        gse = d.treats.all()[0]
        print d.id, \
            "\t", \
            gse.series_id, \
            "\t", \
            gse.species, \
            "\t", \
            gse.factor, \
            "\t", \
            gse.cell_type if gse.cell_type else None, \
            "\t", \
            gse.cell_line if gse.cell_line else None, \
            "\t", \
            gse.tissue_type if gse.tissue_type else None, \
            "\t",
        if gse.factor == None:
            print "None", \
                "\t",
        else:
            if gse.factor.status == "ok":
                print gse.factor.type, \
                    "\t",
            else:
                                print "None", \
                                        "\t",
        if gse.paper == None:
            print "None", \
                "\t", \
                "None", \
                "\t", \
                "None", \
                "\t",
        else:
                print gse.paper, \
                        "\t",
                if gse.paper.journal == None:
                        print "None", \
                        "\t", \
                                        "None", \
                                        "\t",
                else:
                        print gse.paper.journal, \
                                "\t", \
                    gse.paper.journal.impact_factor, \
                    "\t",
    #                   if gse.paper.journal.impact_factor == None:
    #                           print "None", \
    #                     "\t",
                                # else:
                    # print gse.paper.journal.impact_factor, \
                                        # if gse.paper.journal.impact_factor >= 5:
                                                # print gse.paper.journal.impact_factor, \
                                                #       "\t",
                                                # if gse.paper.journal.name == None:
                                                #       print "None", \
                                                #               "\t",
                                                # else:
                                                #       if gse.paper.journal.impact_factor >= 5:
                                                #               print gse.paper.journal.name, \
                                                #                       "\t",
        for t in d.treats.all():
            print t.unique_id,
    if not d.conts.all():
        print "\t",
        print "NoControl",
    else:
        print "\t",
        for c in d.conts.all():
            print c.unique_id,
    if not d.status:
        continue
    else:
        print "\t",
        print d.status
