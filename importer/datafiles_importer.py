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
import re
import tarfile
import time
import shutil
import datetime
import traceback

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

DEFAULT_DIR = "/data/aspuserfiles/dcdropbox/"

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
                tfile = tarfile.open(filepath)
                if "manifest.txt" not in tfile.getnames():
                    failed(filepath)
                    continue
                tmpdir = mktmpdir()
                os.chdir(tmpdir)
                tfile.extractall()
                #read in manifest as a dict
                manifest = readManifest()
                if ("dataset" not in manifest) or ("username" not in manifest):
                    failed(filepath)
                    continue
                #try to get the dataset model
                d = models.Datasets.objects.get(pk=manifest['dataset'])
                u = User.objects.get(username=manifest['username'])
                d.uploader=u
                d.upload_date=datetime.datetime.now()
                for f in manifest:
                    if (f != "dataset") and (f != "username"):
                        #save the files
                        tmp = File(open(manifest[f]))
                        setattr(d, f+"_file", tmp)
                d.save()
                os.chdir(opts.dir)
                shutil.rmtree(tmpdir) #remove the tmp dir
                os.remove(filepath)

                #tmp = File(open(manifest['raw']))
                #d.raw_file = tmp
                #d.save()
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
