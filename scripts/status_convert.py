from datacollection import models

for d in models.Datasets.objects.all():
    if d.status=="info":
        d.status="auto-parsed"
    elif d.status=="new":
        d.status="inherited"
    elif d.status=="valid":
        d.status = "validated"
    d.save()
