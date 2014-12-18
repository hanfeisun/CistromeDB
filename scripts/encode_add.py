from datacollection import models
gsm = []
files = ["human_DHS.txt", "human_meta.txt", "mouse_DHS.txt", "mouse_meta.txt"]
base_dir = "/data/newdc1.4/src/scripts/Encode_Data/"
for f in files:
    with open(base_dir+f) as hD:
        print hD
        for i in hD:
            if i.startswith("#"):
                continue
            # if f.endswith("DHS.txt"):
            #     eles = i.strip().split("\t")
            #     treat = eles[0].split(",")
            #     control= eles[1].split(",")
            #     factor,_ = models.Factors.objects.get_or_create(name=eles[2])
            #     factor.save()
            #     cell_line,_ = models.CellLines.objects.get_or_create(name=eles[4])
            #     cell_line.save()
            #     try:
            #         tissue,_ = models.TissueTypes.objects.get_or_create(name=eles[5])
            #         tissue.save()
            #     except:
            #         tissue = None

            #     if f.startswith("human"):
            #         species = models.Species.objects.get(id=1)
            #     else:
            #         species = models.Species.objects.get(id=2)
            #     new_dataset = models.Datasets.objects.create(status="encode", full_text=" ")
            #     new_dataset.save()

            #     for t in treat:
            #         if t.startswith("GSM"):
            #             sample,_ = models.Samples.objects.get_or_create(unique_id=t)
            #             if tissue:
            #                 sample.tissue_type = tissue
            #             sample.species = species
            #             sample.factor = factor
            #             sample.cell_line=cell_line
            #             sample.status = "encode"

            #             sample.save()
            #             new_dataset.treats.add(sample)
            if f.endswith("meta.txt"):
                eles = i.strip().split("\t")
                treat = eles[0].split(",")
                control= eles[1].split(",")
                factor,_ = models.Factors.objects.get_or_create(name=eles[2].split("_")[0])
                factor.save()
                cell_line,_ = models.CellLines.objects.get_or_create(name=eles[3])
                cell_line.save()
                try:
                    tissue,_ = models.TissueTypes.objects.get_or_create(name=eles[4])
                    tissue.save()
                except:
                    tissue = None

                if f.startswith("human"):
                    species = models.Species.objects.get(id=1)
                else:
                    species = models.Species.objects.get(id=2)
                new_dataset = models.Datasets.objects.create(status="encode", full_text=" ")
                new_dataset.save()

                for t in treat:
                    if t.startswith("GSM"):
                        sample,_ = models.Samples.objects.get_or_create(unique_id=t)
                        if tissue:
                            sample.tissue_type = tissue
                        sample.species = species
                        sample.factor = factor
                        sample.cell_line=cell_line
                        sample.status = "encode"

                        sample.save()
                        new_dataset.treats.add(sample)

                for t in control:
                    print t, "conts"
                    if t.startswith("GSM"):
                        sample,_ = models.Samples.objects.get_or_create(unique_id=t)
                        if tissue:
                            sample.tissue_type = tissue
                        sample.species = species
                        sample.cell_line = cell_line
                        sample.factor,_ = models.Factors.objects.get_or_create(name="Input")
                        sample.status = "encode"
                        sample.save()
                        new_dataset.conts.add(sample)
                new_dataset.save()
