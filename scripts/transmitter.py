__author__ = 'hanfei'
from datacollection.models import Datasets,Samples


for a_dataset in Datasets.objects.all():

    all_treats = a_dataset.treats.all()
    all_control = a_dataset.conts.all()

    if not all_treats:
        continue

    if None in [x.fastq_file_url for x in all_treats] or None in [x.fastq_file_url for x in all_control]:
        continue


    print "["+str(a_dataset.id)+"]"


    for counter,a_sample in enumerate(all_treats):
        counter += 1
        # Start from 1 instead of 0
        assert isinstance(a_sample, Samples)
        print "TREAT_%s_ID = %s" %(counter, a_sample.id)
        print "TREAT_%s_UNIQUE_ID = %s" % (counter, a_sample.unique_id)
        print "TREAT_%s_URL = %s" %(counter, a_sample.fastq_file_url)
        print "TREAT_%s_SPECIES = \"%s\"" %(counter, a_sample.species)
        print ""

    for counter,a_sample in enumerate(all_control):
        counter += 1
        assert isinstance(a_sample, Samples)
        print "CONT_%s_ID = %s" %(counter, a_sample.id)
        print "CONT_%s_UNIQUE_ID = %s" % (counter, a_sample.unique_id)
        print "CONT_%s_URL = %s" %(counter, a_sample.fastq_file_url)
        print "CONT_%s_SPECIES = \"%s\"" %(counter, a_sample.species)
        print ""

    print "\n"

