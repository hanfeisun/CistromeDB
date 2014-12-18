from django.core.management import setup_environ
import sys
sys.path.insert(0,'/data1/newdc1.4/src')
import settings
setup_environ(settings)
from datacollection import models
f = open("sample_info.tsv","wb")
f.write( "\t".join(["SampleID", "UniqueID","Name","Factor","Species","CellLine","CellType","CellPop","Strain","TissueType","Disease","Antibody"]))
for s in models.Samples.objects.all():
    f.write(str(s.id))
    f.write( '\t')
    f.write( str(s.unique_id))
    f.write( '\t')
    f.write( s.name.encode("utf-8"))
    for k in ["factor","species","cell_line","cell_type","cell_pop","strain","tissue_type","disease_state","antibody"]:
        f.write( '\t')
        k_i = getattr(s,k)
        if k_i:
            f.write( k_i.name.encode("utf-8"))
        else:
            f.write( "None")
    f.write('\n')


