#!/usr/bin/python
"""
SYNOPSIS: this script takes a sample id; samples are assumed to have 
valid raw_file_urls.

This script will:
1. try to open a ftp connection to download the sra file
   NOTE: this is complicated b/c the raw_file_urls are not unique filepaths,
   i.e. there's still some hunting after going to the url!
2. will use fastq-dumps (an SRA tool) to convert the SRA to fastq
3. will associate the converted fastq with the raw_file
"""

import os
import sys
import re
from ftplib import FTP
import subprocess

import importer_settings
from django.core.files import File
from django.core.management import setup_environ
sys.path.insert(0, importer_settings.DEPLOY_DIR)
import settings
setup_environ(settings)

from django.core.files import File

from datacollection import models

USAGE = """USAGE: SRADnlr.py [sample id]
Will try to retrieve the SRA file specified by sample.raw_file_url
"""

_fastq_dump_path = os.path.join(settings.DEPLOY_DIR, "importer", "bin",
                                "fastq-dump.2.0.6")

def sraDownload(file_url):
    """Given a SRA ftp file url, e.g. 
    ftp://ftp-trace.ncbi.nih.gov/sra/sra-instant/reads/ByExp/sra/SRX/SRX0\
03/SRX003872/    
    tries to download the file and returns the fp to the file

    NOTE: these links usually don't point to files!  the file is usually in 
    some sub-dir e.g.:
    ftp://ftp-trace.ncbi.nih.gov/sra/sra-instant/reads/ByExp/sra/SRX/SRX0\
03/SRX003872/SRR015157/SRR015157.sra
    So we have to be a little smart about hunting for it
    """

    if file_url.endswith(".sra") or file_url.endswith(".SRA"):
        #direct download
        subprocess.call(["wget", file_url])
        filename = file_url.split("/")[-1]
        f = open(filename, "r")
        f.close()
        return ("", f)
    else:
        #we have to go hunting in the ftp dir
        #print file_url
        parts = file_url.split("/")
        #Gives something like this:
        #[u'ftp:', u'', u'ftp.ncbi.nih.gov', u'pub', u'geo', u'DATA', u'supplementary', u'samples', u'GSM301nnn', u'GSM301351', u'GSM301351.CEL.gz']
    
        server = parts[2]
        path = parts[3:]

        #GET the file!
        ftp = FTP(server)
        ftp.login()
        ftp.cwd("/".join(path))

        #now we have to look for the first sra file in these sub-dirs and try 
        #and try to dnld it        
        _sra_file_pattern = "^(\w+\.)+(sra|SRA)$"
        filename = ""
        sub_path = ""
        while not filename:
            #print sub_path
            ls = ftp.nlst()
            #print ls
            for f in ls:
                if re.match(_sra_file_pattern, f):
                    filename = f
            if not filename:
                #just go down the first dir
                sub_path = os.path.join(sub_path, ls[0])
                ftp.cwd(ls[0])

        #NOTE: this should be saved!!
        new_path = "ftp://%s/%s" % \
            (server, os.path.join("/".join(path), sub_path, filename))
        #print new_path

        f = open(filename, "wb")
        ftp.retrbinary("RETR %s" % filename, f.write)
        f.close()
        ftp.close()

        return (new_path, f)


def main():
    if len(sys.argv) != 2:
        print USAGE
        sys.exit(-1)
    
    sample_id = sys.argv[1]
    sample = models.Samples.objects.get(pk=sample_id)
    
    (new_path, sra_file) = sraDownload(sample.raw_file_url)

    #use the new path for later access
    if new_path:
        sample.raw_file_url = new_path

    #convert the file
    ret_code = subprocess.call([_fastq_dump_path, sra_file.name])
    fastq_filename = sra_file.name.replace("sra", "fastq")
    #associate the file
    sample.raw_file = File(open(fastq_filename))
    sample.status = "downloaded"
    
    sample.save()

if __name__=="__main__":
    main()
