__author__ = 'hanfei'
from datacollection.models import Samples
import json

for a_sample in Samples.objects.all():
    print a_sample
    try:
        if not a_sample.other_ids:
            continue

        other_ids = json.loads(a_sample.other_ids)

        if not other_ids :
            continue

        if not other_ids.get("gse",None):
            continue

        a_sample.series_id = "GSE"+str(other_ids.get("gse")[4:])
        a_sample.save()
        print a_sample.series_id
    except:
        print str(a_sample) + " NIMABI"
        continue