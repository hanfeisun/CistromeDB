gsm = []
files = ["human_DHS.txt", "human_meta.txt", "mouse_DHS.txt", "mouse_meta.txt"]
base_dir = "/data/newdc1.4/src/scripts/Encode_Data/"
for f in files:
    with open(base_dir+f) as hD:
        for i in hD:
            if i.startswith("#"):
                continue
            eles = i.strip().split("\t")
            treat = eles[0].split(",")
            control= eles[1].split(",")
            # print treat
            # print control
            # # print eles
            # print f,
            # print "-"
            gsm += treat
            gsm += control
gsm_final = [i for i in gsm if i!="none" and i!= "NA"]
print len(gsm_final)
from datacollection import models
counter = 0
for i in gsm_final:
    print "here"
    s = models.Samples.objects.filter(unique_id=i)
    for a_s in s:
        counter +=1
        for t in a_s.TREATS.all():
            t.delete()
        for c in  a_s.CONTS.all():
            c.delete()
        a_s.delete()
    print counter
