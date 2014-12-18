from datacollection import models
with open("/data/newdc1.4/src/scripts/Encode_Data/final_cut.txt") as f:
    for i in f:
        eles = i.strip().split("\t")
        name = eles[0]
        cat = eles[1]
        samples = models.Samples.objects.filter(cell_line__name=name)
        if cat=="primaryCells":
            for s in samples:
                print "p"
                s.cell_line = None
                s.cell_type, _ = models.CellTypes.objects.get_or_create(name=name)
                s.save()
        elif cat =="Tissue":
            for s in samples:
                print "t"
                s.cell_line = None
                s.save()
        try:
            models.CellLines.objects.get(name=name).delete()
        except:
            print name
