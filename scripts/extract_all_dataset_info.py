from django.core.management import setup_environ
import sys
sys.path.insert(0,'/data1/newdc1.4/src')
import settings
setup_environ(settings) 
from datacollection import models
print "\t".join(["DatasetID","Treats","Controls"])
for d in models.Datasets.objects.all():
    print d.id,
    print '\t',
    print ",".join([str(i.id) for i in d.treats.all()]),
    print '\t',
    if d.conts.all():
        print ",".join([str(i.id) for i in d.conts.all()])
    else:
        print "NoControl"

