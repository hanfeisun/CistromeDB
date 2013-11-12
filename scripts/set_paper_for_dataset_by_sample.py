__author__ = 'hanfei'
from datacollection.models import Datasets
for a_dataset in Datasets.objects.filter(status=u'info'):
    try:
        a_dataset.paper = a_dataset.treats.all()[0].paper
        a_dataset.save()
    except IndexError:
        print a_dataset
        print "Shit!!"
        continue
    print(a_dataset.paper)
