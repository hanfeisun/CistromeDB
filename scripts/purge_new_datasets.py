from datacollection.models import Datasets


Datasets.objects.filter(status="info").delete()

