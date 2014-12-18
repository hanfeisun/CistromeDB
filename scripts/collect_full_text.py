from datacollection import models
counter = 1
datasets_to_change = models.Datasets.objects.filter(factor__isnull=True)
print "%s datasets"%datasets_to_change.count()
for a_dataset in datasets_to_change:
    a_dataset.save()
    print counter
    print a_dataset
    counter += 1

