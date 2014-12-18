from datacollection.models import Datasets

id_dir_dict = {}

with open("/home/qqin/Workspace/Achieved/DCStat/dc_result_id_directory.txt") as f:
    f.readline()
    for a_line in f:
        _map = a_line.strip().split("\t")
        id_dir_dict[_map[0]] = _map[1].replace("//","/")

for a_dataset in Datasets.objects.all():
    a_dataset.result_folder = id_dir_dict.get(str(a_dataset.id), None)
    if a_dataset.result_folder:
        if a_dataset.status in ["validated", "complete"]:
            a_dataset.status = "complete"
            a_dataset.save()
        else:
            print a_dataset.status
            print a_dataset.result_folder









