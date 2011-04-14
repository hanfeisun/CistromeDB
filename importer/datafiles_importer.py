#!/usr/bin/python
"""
Synopsis: this script checks a given directory for tar or zip packages,
and tries to automatically import the files contained within each package.
This script can/should be set as a cron job that runs every night.

NOTE: the packages must have a manifest.txt file
"""
import os
import sys
import optparse
import ConfigParser
import re
import tarfile
import time
import shutil
import datetime
import traceback
import string

import importer_settings
from django.core.files import File
from django.core.management import setup_environ
sys.path.insert(0, importer_settings.DEPLOY_DIR)
import settings
setup_environ(settings)
from django.contrib.auth.models import User

from datacollection import models

USAGE = """USAGE: datafiles_importer
Options:
         -d - path to the dir which to search for packages
              DEFAULT: /data/aspuserfiles/dcdropbox/
"""

DEFAULT_DIR = "/data/liulab_aspera_dropbox/dcdropbox"

def read_config(configFile):
    """Read configuration file and parse it into a dictionary.
    
    In the dictionary, the key is the section name plus option name like:
    data.data.treatment_seq_file_path.
    NOTE: this is ripped directly from Tao's ChIP-Seq_Pipeline1.py script
    """
    configs = {}
    
    configParser = ConfigParser.ConfigParser()
    
    if len(configParser.read(configFile)) == 0:
        raise IOError("%s not found!" % configFile)
    
    for sec in configParser.sections():
        secName = string.lower(sec)
        for opt in configParser.options(sec):
            optName = string.lower(opt)
            configs[secName + "." + optName] = \
                            string.strip(configParser.get(sec, opt))

    return configs
                                                                
def mktmpdir():
    """Tries to make a temporary working directory; if successful returns
    the directory name"""
    temp_dir = "tmp_%s" % time.time()
    #make the temporary directory and move in
    try:
        os.mkdir(temp_dir)
    except OSError, e:
        os.removedirs(temp_dir)
        os.mkdir(temp_dir)
    return temp_dir

def failed(filepath):
    """IF something fails with the package, e.g. no manifest, or no dataset id
    then we rename the package as [blah].tar.gz.fail"""
    shutil.move(filepath, filepath+".fail")

def readManifest():
    """try to read in manifest.txt and convert the key=value pairs into 
    dictionary entries"""
    f = open("manifest.txt")
    tmp = {}
    for l in f.readlines():
        (key, val) = l.split("=")
        tmp[key.strip()] = val.strip()
    f.close()
    return tmp

#A mapping from summary.txt file fields to dataset model file fields
#NOTE: missing raw file!
_Pipe2Datasets_Dict = [("macs_peaks", "peak_file"),
                       ("macs_xls", "peak_xls_file"),
                       ("macs_summits", "summit_file"),
                       ("macs_treat_wig", "wig_file"),
                       ("macs_control_wig", "control_wig_file"),
                       ("conservation_bmp", "conservation_file"),
                       ("conservation_r", "conservation_r_file"),
                       ("correlation_pdf", "qc_file"),
                       ("correlation_r", "qc_r_file"),
                       ("ceas_pdf", "ceas_file"),
                       ("ceas_r", "ceas_r_file"),
                       ("venn_diagram_png", "venn_file"),
                       ("seqpos_zip", "seqpos_file"),
                       ]

def main():
    parser = optparse.OptionParser(usage=USAGE)
    parser.add_option("-d", "--dir", default=DEFAULT_DIR,
                      help="path to the dir which to search for packages")
    (opts, args) = parser.parse_args(sys.argv)
    #print opts.dir

    cwd = os.getcwd()

    package_pattern = "^.+\.tar.gz$"
    if os.path.exists(opts.dir):
        os.chdir(opts.dir)
        files = os.listdir(opts.dir)
        pkgs = [f for f in files if re.match(package_pattern, str(f))]
        #list all of the tar.gz files in opts.dir
        #print pkgs
        for p in pkgs:
            os.chdir(opts.dir)
            try:
                filepath = os.path.join(opts.dir, p)
                #print filepath
                tfile = tarfile.open(filepath)
                tfile.extractall()
                #NOTE: **important- the tar ball names are ALWAYS assumed to
                #be in this form: sampleN.tar.gz--where N is the sample id;
                #AND the tar ball extracts to a dir called sampleN
                #AND the summary is ALWAYS sampleN_summary.txt
                tmpdir = p.split(".")[0]
                os.chdir(tmpdir)
                
                #read in sampleN_summary.txt
                config = read_config(tmpdir+"_summary.txt")
                #print config
                #for k in config.keys():
                #    if k.startswith("summary"):
                #        print k

                if ("sample.sample_id" not in config) or \
                   ("sample.username" not in config):
                    failed(filepath)
                    continue

                #try to get the dataset model
                d = models.Datasets.objects.get(pk=config['sample.sample_id'])
                u = User.objects.get(username=config['sample.username'])
                d.uploader=u
                d.upload_date=datetime.datetime.now()
                
                #try to set the dataset fields
                for f in _Pipe2Datasets_Dict:
                    if "sample."+f[0] in config:
                        setattr(d, f[1], File(open(config["sample."+f[0]])))
                d.save()

                #try to store the summary info                
                if ('summary.total_peaks' in config) and \
                   ('summary.peaks_overlapped_with_dhss' in config):
                    #print config['summary.total_peaks']
                    #print config['summary.peaks_overlapped_with_dhss']
                    dhs = models.DatasetDhsStats()
                    dhs.dataset = d
                    dhs.total_peaks = config['summary.total_peaks']
                    dhs.peaks_in_dhs = config['summary.peaks_overlapped_with_dhss']
                    dhs.save()
                
                
                os.chdir(opts.dir)
                shutil.rmtree(tmpdir) #remove the tmp dir

                #move the filepath to tar.gz.processed
                shutil.move(filepath, filepath+".processed")
                        
            except: 
                #something went wrong
                #NOTE: if the import breaks, mv the file to .tar.gz.failed
                print "Exception in user code:"
                print '-'*60
                traceback.print_exc(file=sys.stdout)
                print '-'*60
                failed(filepath)
    

if __name__=="__main__":
    main()
