__author__ = 'hanfei'
from datacollection.models import Datasets

cleaned_cnt = 0
for a_dataset in Datasets.objects.filter(status=u'info'):
    if len(a_dataset.treats.all()) == 0 and len(a_dataset.conts.all()) == 0 :
        a_dataset.delete()





