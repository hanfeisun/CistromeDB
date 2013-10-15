"""Library to interface with the SRA repository"""

import os
import re
import sys
import urllib
import traceback
import datetime

import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString

#AUTO-load classifiers
#a trick to get the current module 
_modname = globals()['__name__']
_this_mod = sys.modules[_modname]

_ppath = "/".join(_this_mod.__file__.split("/")[:-1])

# #CAN drop this if this is an app!
# DEPLOY_DIR="/home/lentaing/envs/newdc1.4/src"
# sys.path.insert(0, DEPLOY_DIR)
# from django.core.management import setup_environ
# from django.utils.encoding import smart_str
# import settings
# setup_environ(settings)

from datacollection import models

#OBSOLETE: replaced by geo.getGDSSamples
def getSRASamples():
    """Will run the predefined query and return a list of SRA ids    
    """
    #REAL URL
    URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=sra&term=(%22strategy%20chip%20seq%22[Properties])%20AND%20(homo%20sapiens[Organism]%20OR%20mus%20musculus[Organism])&retmax=100000&usehistory=y"

    #TEST URL
    #URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=sra&term=(%22strategy%20chip%20seq%22[Properties])%20AND%20(homo%20sapiens[Organism]%20OR%20mus%20musculus[Organism])&retmax=10&usehistory=y"

    try:
        f = urllib.urlopen(URL)
        root = ET.fromstring(f.read())
        f.close()

        #Get the IDList
        tmp = root.findall("IdList/Id")
        return [i.text for i in tmp]
    except:
        print "Exception in user code:"
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
        return []

def getSraXML(accession):
    """HANDLES SRA XML records--i.e. our SRA XML librarian!
    Given an accession #, tries to look for the record locally,
    IF not found, then makes a remote call to fetch it

    returns the sra record as xml string

    NOTE: this url is wrong!
    http://www.ncbi.nlm.nih.gov/sra?term=378792[uid]&report=FullXml
    INSTEAD use efetch:
    http://www.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=sra&id=378792
    """
    docString = None
    path = os.path.join(_ppath, "sra")
    if not os.path.exists(path):
        os.mkdir(path)
    subdir = os.path.join(path, accession[:3])
    if not os.path.exists(subdir):
        os.mkdir(subdir)
    path = os.path.join(subdir, "%s.xml" % accession)

    if os.path.exists(path):
        f = open(path)
        docString = f.read()
        f.close()
    else:
        URL = "http://www.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=sra&id=%s" % accession
        try:
            urlf = urllib.urlopen(URL)
            docString = urlf.read()
            urlf.close()
            #write to file
            f = open(path, "w")
            f.write(docString)
            f.close()
        except:
            print "Exception in user code:"
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
            docString = None

    return docString

def getSRA_downloadLink(sraXML):
    """makes an aspera download link
    Given a xml, looks for:
    <RUN_SET>
    <RUN alias="GSM1126513_r1" accession="SRR830943" center_name="GEO" total_spots="43012198" total_bases="6537854096" size="3933810695" load_done="true" published="2013-04-22 15:13:59" is_public="true" cluster_name="public" static_data_available="1">

    NOTE: this has other useful info, e.g. size, total_bases, 
    """
    ret = ""
    root = ET.fromstring(sraXML)
    tmp = root.findall("EXPERIMENT_PACKAGE/RUN_SET/RUN")
    if tmp:
        attrib = tmp[0].attrib
        if "accession" in attrib and attrib["is_public"] == "true":
            acc = attrib["accession"]
            #NOTE: full path is: anonftp@ftp-private.ncbi.nlm.nih.gov: + PATH
            #EXAMPLE:/sra/sra-instant/reads/ByRun/sra/SRR/SRR007/SRR007437/SRR007437.sra
            ret = "/sra/sra-instant/reads/ByRun/sra/SRR/"+acc[:6]+"/"+acc+"/"+acc+".sra"
    return ret

