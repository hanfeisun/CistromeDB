"""
SYNOPSIS: tries to generate a download script in a given working directory

Taken from RunSHGenerator.py in pipeline
"""

import os
import settings

_SRADnldr_PATH = os.path.join(settings.DEPLOY_DIR, "importer", "SRADnldr.py")

def generateDaemonizer(working_dir="."):
    """generates the python script that will daemonize the call to run script
    """
    py_template = """#!/usr/bin/python

import daemon
import subprocess

with daemon.DaemonContext(working_directory="."):
    proc = subprocess.Popen(["nohup", "bash", "run.sh"])
"""
    py_sh = open(os.path.join(working_dir, "daemonize.py"), "w")
    py_sh.write(py_template)
    
    py_sh.close()
    return py_sh

def generate(dataset, user, working_dir="."):
    """tries to generate a file called run.sh:
    #!/bin/bash
    
    #1. get the file
    #2. convert the file to fasta
    #3. try to import the fasta file
    #4. on completion, try to email the user via sendmail
    """
    email_template = """to:%s\nfrom:%s\nsubject:%s\n\n%s"""
    email = email_template % (user.email, "cistrome_admin@jimmy.harvard.edu",
                              "Datacollection Download - Dataset %s" % dataset.id,
                              "the download of dataset %s is done"%dataset.id)

    script_template = """#!/bin/bash

#1. run SRADndr
%s %s

#2. on completion, email notify the user
echo '%s' | sendmail -t
"""

    if not os.path.exists(working_dir):
        os.makedirs(working_dir)
    
    run_sh = open(os.path.join(working_dir, "run.sh"), "w")
    run_sh.write(script_template % (_SRADnldr_PATH, dataset.id, email))
    run_sh.close()
    
    #generate the daemonize wrapper
    py_sh = generateDaemonizer(working_dir)

    return run_sh
