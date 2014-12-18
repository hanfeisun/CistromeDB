from datacollection.models import Datasets

dataset_status_d = {}
with open("/home/qwu/newdc/files/datasets_IF5_20140827.txt") as f:
    f.readline()
    for a_line in f:
        splited = a_line.split("\t")
        dataset_status_d[splited[0].strip()] = splited[-1].strip()

print dataset_status_d
for a_dataset in Datasets.objects.all():
    a_dataset.status = dataset_status_d.get(str(a_dataset.id), "?")
    print a_dataset.status
    a_dataset.save()


