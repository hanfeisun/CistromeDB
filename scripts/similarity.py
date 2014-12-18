import glob
from subprocess import check_output
import json

intersectCMD = "intersectBed -u -a %s -b %s | wc -l"
result_path = "/data/home/hanfei/dc_intersect_result/"
import_bed_path = "/data/home/qqin/Workspace/Achieved/DCjsons/Codes/top1000peak_directory.txt"
# import_bed_path = "/data/home/hanfei/text.txt"
class BedRepository:
    def __init__(self):
        self.repo = {}
        self.species = {}

    def import_bed(self, import_bed_path):
        with open(import_bed_path) as ibp:
            #skip first line
            ibp.readline()
            for a_line in ibp:
                id,bed_path = a_line.strip().split()
                self.repo[id] = bed_path
                if "hg38" in bed_path:
                    self.species[id] = "hg38"
                elif "mm10" in bed_path:
                    self.species[id] = "mm10"

    def has(self, one_id):
        return self.repo.has(one_id)

    def get_path(self, one_id):
        return self.repo.get(one_id, None)

    def get_species(self, one_id):
        return self.species[one_id]

    def get_ids_by_species(self, species):
        return [i[0] for i in self.species.items() if i[1]==species]


    def get_all_ids(self):
        return self.repo.keys()

    def make_intersect_json(self, one_path, result_path, species):

        json_rtn = []

        species_ids = self.get_ids_by_species(species)
        ten_percent = len(species_ids) / 10
        for idx, another_id in enumerate(species_ids):
            a_path = self.get_path(another_id)
            if a_path == one_path:
                continue
            intersect_cnt = self.get_intersect_cnt(one_path, a_path)
            json_rtn.append([another_id, intersect_cnt])
            if idx%ten_percent == 0:
                print "%s / %s" %(idx,  len(species_ids))

        print one_path

        with open(result_path, "w") as rp:
            json.dump(json_rtn, rp)
        # return json path

    def get_intersect_cnt(self, one_path, another_path):
        return int(check_output(intersectCMD%(one_path, another_path), shell=True))

    # def get_intersect_cnt(self, one_path, another_path):
    #     print intersectCMD%(one_path, another_path)
    #     raise




class ResultPathManager:
    def __init__(self, root):
        self.root = root


    def make_result_path(self, id):
        return self.root + str(id) + "_intersect.json"

    def make_ranked_result_path(self, id):
        return self.root + str(id) + "_intersect_ranked.json"


class ResultRanker:
    def __init__(self, result_path):
        self.result_path = result_path

    def make_ranked_json(self, result_path):
        # Return json path
        pass






bed_repository = BedRepository()
result_manager = ResultPathManager(result_path)
bed_repository.import_bed(import_bed_path)
print("import successfully")

all_ids = bed_repository.get_all_ids()

for idx,an_id in enumerate(all_ids):
    print("an id")
    a_path = bed_repository.get_path(an_id)
    a_result_path = result_manager.make_result_path(an_id)
    a_species = bed_repository.get_species(an_id)

    a_ranked_result_path = result_manager.make_ranked_result_path(an_id)
    bed_repository.make_intersect_json(a_path, a_result_path, a_species)
    print a_result_path
    print "%s / %s" %(idx, len(all_ids))
    # ResultRanker(a_result_path).make_ranked_json(a_ranked_result_path)
    # break




# intersect(import_bed_path)
