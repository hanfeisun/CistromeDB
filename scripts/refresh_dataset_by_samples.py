from datacollection import models

for a_sample in models.Samples.objects.all():
    a_sample.save()
