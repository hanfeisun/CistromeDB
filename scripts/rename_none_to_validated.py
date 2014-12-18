from django.db.models import Q

__author__ = 'hanfei'
from datacollection.models import *

for m in (CellLines, CellPops, CellTypes, TissueTypes):
    print m
    print m.objects.filter(status=None).count()
    print m.objects.filter(status__isnull=True).count()

    for record in m.objects.filter(Q(status="ok")|Q(status="")):
        record.status = "ok"
        record.save()