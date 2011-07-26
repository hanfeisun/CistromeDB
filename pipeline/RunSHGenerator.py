"""
SYNPOSIS: tries to generate run.sh files in the pipeline working directories
"""

import os
import settings

#Assumes that pipeline path is the parent dir of settings.CONF_TEMPLATE_DIR
_PIPELINE_PATH = "/".join(settings.CONF_TEMPLATE_DIR.split("/")[:-1])
_ChipSeqPipeline_PATH = os.path.join(_PIPELINE_PATH, "ChIPSeqPipeline.py")
_Importer_PATH = os.path.join(settings.DEPLOY_DIR, "importer", 
                              "datafiles_importer.py")

def generateDaemonizer(dir="."):
    """generates the python script that will daemonize the call to run script
    """
    py_template = """#!/usr/bin/python

import daemon
import subprocess

with daemon.DaemonContext(working_directory="."):
    proc = subprocess.Popen(["nohup", "bash", "run.sh"])
"""
    py_sh = open(os.path.join(dir, "daemonize.py"), "w")
    py_sh.write(py_template)
    
    py_sh.close()
    return py_sh
    

def generate(sample, conf_file, user, dir="."):
    """tries to generate a file called run.sh:
    #!/bin/bash
    
    #1. run the pipeline
    python [pipeline tool] [conf file]
    
    #2. on completion, try to email the user via sendmail
    """
    email_template = """to:%s\nfrom:%s\nsubject:%s\n\n%s"""
    email = email_template % (user.email, "cistrome_admin@jimmy.harvard.edu",
                              "Datacollection Run - Sample %s" % sample.id,
                              "your run on sample %s is complete" % sample.id)

    script_template = """#!/bin/bash

#1. run the pipeline
python %s %s

#2. TEST for success--if the tar.gz is generated
if [ -e %s.tar.gz ]
then
#TRY import
%s -d %s

fi 

#3. on completion, email notify the user
echo '%s' | sendmail -t
"""
    
    run_sh = open(os.path.join(dir, "run.sh"), "w")
    run_sh.write(script_template % (_ChipSeqPipeline_PATH, conf_file.name, 
                                    "sample%s"%sample.id, _Importer_PATH, dir,
                                    email))

    run_sh.close()
    
    #generate the daemonize wrapper
    py_sh = generateDaemonizer(dir)

    return run_sh
