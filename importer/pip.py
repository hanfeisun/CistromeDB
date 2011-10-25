#!/usr/bin/python
"""
Synopsis: pip is a program that tries to download all of the datasets
associated with a given paper in the newdc
"""

import sys
import os
import urllib

#NOTE: pip depends on import_settings to define NEWDC_DIR
import importer_settings
sys.path.insert(0, importer_settings.DEPLOY_DIR)

from django.core.management import setup_environ
from django.core.files import File

import settings
import datacollection.email as email

setup_environ(settings)


from datacollection import models

USAGE = "usage: %prog [paper_id]" 
def main():
    """
    1. tries to download the files associated with the paper via ftp
    2. once the downloads are complete:
       a. updates the paper's status
       b. emails the paper's user
    """
    #print default_storage.location
    if len(sys.argv) > 1:
        p = models.Papers.objects.get(pk=sys.argv[1])
        dsets = models.Datasets.objects.filter(paper=p)
        for d in dsets:
            if not d.file: #blank file so we need to retrieve it
                #note: there is a redundancy, first we write the bytes to
                #a tmp file, then we read it in to save it.
                (filename, headers) = urllib.urlretrieve(d.file_url)
                fname = d.file_url.split("/")[-1:][0]
                #NOTE: since upload_to is defined in datacollection.models,
                #it automatically stores the file in the correct place
                d.file.save(fname, File(open(filename)))
                d.status = "downloaded"
                d.save()
        #Update the paper's status to "downloaded" and email the user
        p.status = "downloaded"
        p.save()
        msg = "The dc has completed the download of all of the dataset files for paper pmid %s." % p.pmid
        email.newdc_email("Paper PMID:%s datasets download complete" % p.pmid,
                          msg, [p.user.email])
            
if __name__=="__main__":
    main()
    
