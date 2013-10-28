"""Library to interface with the GEO (GDS- GEO DataSets) repository"""

import os
import re
import sys
import urllib
import traceback
import datetime
import time
import enchant
from classifiers import *

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from xml.dom.minidom import parseString

#AUTO-load classifiers
#a trick to get the current module
_modname = globals()['__name__']
_this_mod = sys.modules[_modname]

_ppath = "/".join(_this_mod.__file__.split("/")[:-1])

d = enchant.Dict("en_US")
import json
# #CAN drop this if this is an app!
# DEPLOY_DIR="/home/lentaing/envs/newdc1.4/src"
# sys.path.insert(0, DEPLOY_DIR)
# from django.core.management import setup_environ
# from django.utils.encoding import smart_str
# import settings
# setup_environ(settings)
from django.utils.encoding import smart_str

from datacollection import models

#dynamically load classifiers
#import classifiers
import sra
import pubmed

### HELPER fns
def getFromPost(geoPost, cat):
    """tries to search for cat(VALUE) returns VALUE if found, otherwise ""
    NOTE: categories can be in UPPER or lowercase, eg. TITLE or title
    """
    m = re.search("%s\((.+)\)" % cat.upper(), geoPost)
    if m:
        return m.group(1)
    else:
        return ""


def cleanCategory(s):
    """Given a string, replaces ' ' with '_'
    '/', '&', '.', '(', ')'with ''
    """
    tmp = s.replace(" ", "_")
    for bad in ['/', '&', '.', '(', ')', ',']:
        tmp = tmp.replace(bad, "")
    return tmp


def isXML(doc):
    """TEST if it is a valid geo XML record
    NOTE: first lines are-
    <?xml version="1.0" encoding="UTF-8" standalone="no"?>
    """
    f = doc.split("\n")
    return f[0].strip() == """<?xml version="1.0" encoding="UTF-8" standalone="no"?>"""


def readGeoXML(path, docString=None):
    """
    Input: a file path or a string--default is to use the path

    Tries to read in the geo xml record,
    **KEY: REMOVES the xmlns line
    Returns the xml record text WITHOUT the xmlns line!!!
    """
    if docString:
        f = docString.split("\n")
    else:
        f = open(path)

    tmp = []
    for l in f:
        if l.find("xmlns=\"http://www.ncbi.nlm.nih.gov/geo/info/MINiML\"") == -1:
            tmp.append(l)

    if not docString:
        f.close()

    return "".join(tmp)

### GDS interface
def getGDSSamples():
    """Will run the predefined query and return a list of GDS ids
    NOTE: this returns ALL GDS samples which are of SRA type i.e.
    ALL CHIP-SEQ, RNA-SEQ, etc.
    """
    #expireDate = now - 90 days in seconds
    #ref: http://stackoverflow.com/questions/7430928/python-comparing-date-check-for-old-file
    _expireDate = time.time() - 60 * 60 * 24 * 90

    ret = []

    #TRY: to read a file first -- IF IT IS NOT STALE
    path = os.path.join(_ppath, "gdsSamples.txt")
    if os.path.exists(path) and not os.path.getctime(path) < _expireDate:
        f = open(path)
        for l in f:
            ret.append(l.strip())
        f.close()
    else:
        #REFRESH!

        #REAL URL
        URL = """http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=SRA[Sample Type] AND gsm[Entry Type] AND ("homo sapiens"[Organism] OR "mus musculus"[Organism])&retmax=100000"""

        #TEST URL
        #URL = """http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=SRA[Sample Type] AND gsm[Entry Type] AND ("homo sapiens"[Organism] OR "mus musculus"[Organism])&retmax=10"""

        try:
            #print "getGDSSample: %s" % URL
            f = urllib.urlopen(URL)
            root = ET.fromstring(f.read())
            f.close()

            #Get the IDList
            tmp = root.findall("IdList/Id")
            ret = [i.text for i in tmp]

            #write to disk
            f = open(path, "w")
            for l in ret:
                f.write("%s\n" % l)
            f.close()
        except:
            print "Exception in user code:"
            print '-' * 60
            traceback.print_exc(file=sys.stdout)
            print '-' * 60

    return ret

### Translation fns
def gsm_idToAcc(gdsId):
    """Given a GDS id, e.g. 300982523, tries to give a GDS accession, e.g.
    GSM982523

    NOTE: there is an algorithm: acc = "GSM"+gdsId[1:] (strip leading 0s)
    """
    #Cut = dropping of the "3" (which indicates sample) and removal of leading
    #leading 0s
    cut = gdsId[1:].lstrip("0")
    return "GSM%s" % cut


def gse_idToAcc(gdsId):
    """Given a GDS id, e.g. 200030833, tries to give a GDS accession, e.g.
    GSE30833

    NOTE: there is an algorithm: acc = "GSE"+gdsId[1:] (strip leading 0s)
    """
    #Cut = dropping of the "2" (which indicates series) and removal of leading
    #leading 0s
    cut = gdsId[1:].lstrip("0")
    return "GSE%s" % cut

### Librarian fns
def gsmToGse(gsmid):
    """Given a gsmid, will try to get the geo series id (GSE) that the
    sample is associated with; if it is associated with several GSEs, then
    returns the first.

    STORES the GSE ID, e.g. 200030833 in the file
    NOTE: if we want GSEs then we need to translate IDs to GSEXXXXX just
          like we do for GSMs above

    uses this query:
    http://www.ncbi.nlm.nih.gov/gds/?term=gse%5BEntry+Type%5D+AND+GSM764990%5BGEO+Accession%5D&report=docsum&format=text
    """
    ret = None
    path = os.path.join(_ppath, "GSM_GSE")
    if not os.path.exists(path):
        os.mkdir(path)
    subdir = os.path.join(path, gsmid[:7])
    if not os.path.exists(subdir):
        os.mkdir(subdir)
    path = os.path.join(subdir, "%s.txt" % gsmid)
    if os.path.exists(path):
        f = open(path)
        ret = f.read().strip()
        f.close()
    else:
        #This URL is slow!
        #NOTE: for every ncbi query, try to find the eutils equivalent!
        #--it's faster
        #URL = "http://www.ncbi.nlm.nih.gov/gds/?term=gse[Entry Type] AND %s[GEO Accession]&report=docsum&format=text" % gsmid
        URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gds&term=gse[Entry Type] AND %s[GEO Accession]" % gsmid

        try:
            #print "gsmToGse: %s" % URL
            urlf = urllib.urlopen(URL)
            root = ET.fromstring(urlf.read())
            urlf.close()

            #Get the IDList
            tmp = root.findall("IdList/Id")
            if tmp:
                ret = tmp[0].text.strip()
                f = open(path, "w")
                f.write(ret)
                f.close()

                #FIRST URL
                # m = re.search("ID:\ (\d+)", urlf.read())
                # urlf.close()
                # if m:
                #     ret = m.group(1).strip()
                #     f = open(path, "w")
                #     f.write(ret)
                #     f.close()
        except:
            print "gsmToGse"
            print "URL is" + URL
            print '-' * 60
            traceback.print_exc(file=sys.stdout)
            print '-' * 60

    return ret


def gseToPubmed(gseid):
    """Given a gseid, will try to get the pubmed id
    """
    ret = None
    path = os.path.join(_ppath, "GSE_PUB")
    if not os.path.exists(path):
        os.mkdir(path)
    subdir = os.path.join(path, gseid[:6])
    if not os.path.exists(subdir):
        os.mkdir(subdir)
    path = os.path.join(subdir, "%s.txt" % gseid)
    if os.path.exists(path):
        f = open(path)
        ret = f.read().strip()
        f.close()
    else:
        URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?id=%s&db=pubmed&dbfrom=gds" % gseid
        try:
            #print "gseToPubmed: %s" % URL
            urlf = urllib.urlopen(URL)
            root = ET.fromstring(urlf.read())
            urlf.close()

            #Get the IDList
            tmp = root.findall("LinkSet/LinkSetDb/Link/Id")
            if tmp:
                ret = tmp[0].text.strip()
                f = open(path, "w")
                f.write(ret)
                f.close()
        except:
            print "gsmToGse"
            print '-' * 60
            traceback.print_exc(file=sys.stdout)
            print '-' * 60
    return ret


def gsmToSra(gsmid):
    """Given a gsm id, will try to get an SRA id, using this query:
    http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=sra&term=GSM530220 to get the SRA id

    Returns the SRA id corresponding to the GSM, None otherwise
    """
    ret = None
    path = os.path.join(_ppath, "GSM_SRA")
    if not os.path.exists(path):
        os.mkdir(path)
    subdir = os.path.join(path, gsmid[:7])
    if not os.path.exists(subdir):
        os.mkdir(subdir)
    path = os.path.join(subdir, "%s.txt" % gsmid)

    if os.path.exists(path):
        f = open(path)
        ret = f.read().strip()
        f.close()
    else:
        URL = "http://www.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=sra&term=%s" % gsmid
        try:
            #print "gsmToSra: %s" % URL
            urlf = urllib.urlopen(URL)
            root = ET.fromstring(urlf.read())
            urlf.close()

            #Get the IDList--should just be one
            tmp = root.findall("IdList/Id")
            if tmp:
                ret = tmp[0].text.strip()
                f = open(path, "w")
                f.write(ret)
                f.close()
        except:
            print '-' * 60
            traceback.print_exc(file=sys.stdout)
            print '-' * 60
    return ret


def getGeoXML(accession):
    """HANDLES GEO XML records--i.e. our GEO XML librarian!
    Given a GEO ACCESSION ID, return the xml record for it
    (making the urllib call)"""

    #path pattern: EXAMPLE-GSM1126513 geo/GSM1126/GSM1126513
    path = os.path.join(_ppath, "geo")
    if not os.path.exists(path):
        os.mkdir(path)
    subdir = os.path.join(path, accession[:7])
    if not os.path.exists(subdir):
        os.mkdir(subdir)
    path = os.path.join(subdir, "%s.xml" % accession)

    if os.path.exists(path):
        f = open(path)
        docString = f.read()
        f.close()
    else:
        #print accession
        URL = "http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=%s&view=quick&form=xml&targ=self" % accession

        try:
            #print "getGeoXML: %s" % URL
            urlf = urllib.urlopen(URL)
            docString = urlf.read()
            urlf.close()
            if isXML(docString):
                #write to file
                f = open(path, "w")
                f.write(docString)
                f.close()
            else:
                print "ERROR: accession is NOT xml"
                return None

        except:
            print "Exception in user code:"
            print '-' * 60
            traceback.print_exc(file=sys.stdout)
            print '-' * 60
            docString = None
    return docString


def parseGeoInfo(accession):
    """parse necessary information (detailed description from the Geo XML file"""
    xmlString = readGeoXML(None, getGeoXML(accession))
    tree = ET.fromstring(xmlString)
    ret = {}
    for node in tree.findall("Sample/Channel/Characteristics"):
        ret[node.get("tag")] = node.text.strip()
    ret["source name"] = tree.find("Sample/Channel/Source").text.strip()
    return ret


def postProcessGeo(accession, docString=None):
    """post processes the GEO record to feed into the classifiers
    uses docString IF it is available, otherwise will read the record
    """
    #ignore these tags
    ignore = ["Growth-Protocol", "Extract-Protocol", "Treatment-Protocol"]
    _thresh = 10 #max 10 words

    path = os.path.join(_ppath, "geoPost")
    if not os.path.exists(path):
        os.mkdir(path)
    subdir = os.path.join(path, accession[:7])
    if not os.path.exists(subdir):
        os.mkdir(subdir)
    path = os.path.join(subdir, "%s.txt" % accession)

    if os.path.exists(path):
        f = open(path)
        docString = f.read()
        f.close()
        return docString
    else:
        #need to build the doc
        if not docString:
            #read the document from geo
            docString = getGeoXML(accession)
            #process the string
        text = readGeoXML(None, docString=docString)

        try:
            root = ET.fromstring(text)
        except:
            print "Could not parse: %s" % accession
            print '-' * 60
            traceback.print_exc(file=sys.stdout)
            print '-' * 60
            return None

        #3. collect all of the information under Sample/Channel
        tmp = []

        #Things in sample to get:
        ls = ['Title', 'Source', 'Library-Strategy', 'Library-Source',
              'Library-Selection', 'Supplementary-Data']
        for t in ls:
            tag = root.findall("Sample/%s" % t)
            for tt in tag:
                tmp.append("%s(%s)" % (t.upper(), tt.text.strip().upper()))

        channels = root.findall("Sample/Channel")
        for c in channels:
            for child in c:
                category = ""

                if child.tag in ignore:
                    continue

                #Special case: Characteristic--take the tag attrib
                if child.tag == "Characteristics":
                    if "tag" in child.attrib and child.attrib["tag"]:
                        category = child.attrib["tag"].lstrip().rstrip()
                else:
                    category = child.tag.lstrip().rstrip()

                #convert categories like "cell line" to "CELL_LINE"
                #tmp.append("%s(%s)" % (category.replace(" ","_").upper(),
                #                       child.text.strip()))
                val = child.text.strip()
                #THRESHOLD: values can be at most 10 words
                if len(val.split()) <= _thresh:
                    tmp.append("%s(%s)" % (cleanCategory(category).upper(),
                                           val.upper()))
                else:
                    #take first 10 words
                    tmp.append("%s(%s)" % (cleanCategory(category).upper(),
                                           " ".join(val.split()[:_thresh]).upper()))


        #4. write the information to file
        f = open(path, "w")
        f.write("%s" % smart_str("\n".join(tmp)))
        f.close()

        return "\n".join(tmp)

### Syncing fns
def syncGeo_GeoPost():
    """will ensure that the records in geo are post processed
    Returns a list of newly created records
    """
    ret = []
    p = os.path.join(_ppath, "geo")
    for root, dirs, files in os.walk(p):
        for fname in files:
            path = os.path.join(root, fname)
            acc = fname.split(".")[0]
            dest = os.path.join(_ppath, "geoPost", acc[:7], "%s.txt" % acc)
            if not os.path.exists(dest):
                #update geoPost
                if postProcessGeo(acc):
                    ret.append(acc)
    return ret


def syncGeo_SRA():
    """will try to ensure that there is one SRA record for every geo record
    KEY: use this to query the SRA db- see gsmToSra
    http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=sra&term=GSM530220 to get the SRA id

    Returns a list of newly created records (in SRA)
    """
    ret = []
    p = os.path.join(_ppath, "geo")
    for root, dirs, files in os.walk(p):
        for fname in files:
            path = os.path.join(root, fname)
            gsm = fname.split(".")[0]
            sraId = gsmToSra(gsm)

            if sraId:
                dest = os.path.join(_ppath, "sra", sraId[:3], "%s.xml" % sraId)
                if not os.path.exists(dest):
                    #create the new record
                    tmp = sra.getSraXML(sraId)
                    if tmp:
                        ret.append(sraId)
    return ret


def syncSRA_Geo():
    """
    NOTE: this fn is NOT as important as syncGeo_SRA b/c Geo is our
    primary model!!!

    will try to ensure that there is one Geo record for every SRA record
    NOTE: tries to find the GSM first in the GSM_SRA map, then in the SRA recrd

    Returns a list of newly created records (in GEO)
    """
    #relies on the GSM_SRA map first
    #1. load the map
    _map = {}
    p = os.path.join(_ppath, "GSM_SRA")
    for root, dirs, files in os.walk(p):
        for fname in files:
            path = os.path.join(root, fname)
            gsm = fname.split(".")[0]
            f = open(path)
            sraId = f.read().strip()
            f.close()
            _map[sraId] = gsm

    #2. check the sra db
    ret = []
    p = os.path.join(_ppath, "sra")
    for root, dirs, files in os.walk(p):
        for fname in files:
            gsm = None
            path = os.path.join(root, fname)
            sraId = fname.split(".")[0]
            if sraId in _map:
                gsm = _map[sraId]
            else:
                # try to get the gsm from the file:
                docString = sra.getSraXML(sraId)
                #try to grep the GSMid
                m = re.search("GSM\d+", docString)
                if m:
                    gsm = m.group(0)

            if gsm:
                dest = os.path.join(_ppath, "geo", gsm[:7], "%s.xml" % gsm)
                if not os.path.exists(dest):
                    if getGeoXML(gsm):
                        ret.append(gsm)
    return ret


def syncGSM_GSE():
    """will ensure that the records in geo have a gse id
    Returns a list of newly created records
    """
    ret = []
    p = os.path.join(_ppath, "geo")
    for root, dirs, files in os.walk(p):
        for fname in files:
            path = os.path.join(root, fname)
            acc = fname.split(".")[0]
            if acc:
                dest = os.path.join(_ppath, "GSM_GSE", acc[:7], "%s.txt" % acc)
                if not os.path.exists(dest):
                    #"update GSM_GSE"
                    if gsmToGse(acc):
                        ret.append(acc)
    return ret


def syncGSE_PUB():
    """will ensure that every gse record have a pubmed id
    Returns a list of newly created records
    """
    ret = []
    p = os.path.join(_ppath, "GSM_GSE")
    for root, dirs, files in os.walk(p):
        for fname in files:
            path = os.path.join(root, fname)
            f = open(path)
            acc = f.read().strip()
            f.close()
            dest = os.path.join(_ppath, "GSE_PUB", acc[:6], "%s.txt" % acc)
            if not os.path.exists(dest):
                #update GSE_PUB
                if gseToPubmed(acc):
                    ret.append(acc)
    return ret


def getGeoSamples_byType(ddir="geo", ttype="ChIP-Seq", refresh=False):
    """A filter for our Geo model; searches our db for the specific sample
    type.
    NOTE: hones in on Library-Strategy tag

    Returns a list of samples fitting the specified

    NOTE: building this up takes time, around 10 secs almost 1 minute!
    TRY: caching the result, reading from a cached file takes only 1 minute
    Store them in files by the .ttype--in the local dir
    """
    ret = []
    #check for a cached file:
    p = os.path.join(_ppath, ddir, ".%s" % ttype)
    if not refresh and os.path.exists(p):
        f = open(p)
        for l in f:
            ret.append(l.strip())
        f.close()
    else:
        #NEED to generate the file, and make the call recursively
        #actually, just one level of recursion b/c geo is pretty flat
        p = os.path.join(_ppath, ddir)
        ls = os.listdir(p)
        for df in ls:
            path = os.path.join(p, df)
            if os.path.isfile(path): #it's a file--check if it's ChIP-Seq
                acc = df.split(".")[0]
                #NOTE: we need readGeoXML to process
                text = readGeoXML(path)

                try:
                    rt = ET.fromstring(text)
                    #check for Library-Strategy
                    tag = rt.findall("Sample/Library-Strategy")
                    if tag and tag[0].text.strip() == ttype:
                        #It's a match!
                        ret.append(acc)
                except:
                    #ignored!
                    pass
            else:
                #it's a dir recur
                newd = os.path.join(ddir, df)
                ret.extend(getGeoSamples_byType(newd, ttype, refresh))

        #write the local file:
        f = open(os.path.join(_ppath, ddir, ".%s" % ttype), "w")
        for gsm in ret:
            f.write("%s\n" % gsm)
        f.close()
    return ret


def parseAntibody(description_dict):
    """Given a geoPost, will 1. try to parse out the antibody information
    2. create the new antibody if necessary with the name as:
    VENDOR Catalog# (TARGET) OR
    VENDOR Catalog# --if there is no target OR
    TARGET --if there is no vendor info

    To do this we key in on some key concepts

    Returns the sample's antibody, None otherwise
    """
    print description_dict
    targetFlds = ["antibody source","chip antibody", "antibody"]

    vendorFlds = ["antibody vendorname", "chip antibody provider",
                  "antibody vendor", "antibody manufacturer",
                  "chip antibody vendor", "chip antibody manufacturer", "antibody vendorcatalog#",
                  "antibody vendor and catalog number", "antibody vendor/catalog", "antobody vendor/catalog#"
                  ]
    catalogFlds = ["antibody vendorid", "chip antibody catalog",
                   "antibody CATALOG NUMBER","chip antibody cat #", "antibody catalog #"]
    lotFlds = ["chip antibody lot #"]

    #1. try to get the values
    vals = [None, None, None, None]
    used_fld = []
    for (i, ls) in enumerate([targetFlds, vendorFlds, catalogFlds, lotFlds]):
        for f in ls:
            tmp = description_dict.get(f)
            if tmp:
                vals[i] = tmp
                used_fld.append(f)
                break

    #2. compose the antibody name
    (target, vendor, cat, lot) = tuple(vals)

    if target and "input" in target.lower():
        ret, created = models.Antibodies.objects.get_or_create(name="input")
        return ret

    name_list = []

    def if_match_then_get(keyword, current_key):
        if keyword in current_key:
            current_value = description_dict[current_key]
            if current_value and current_key not in used_fld:
                used_fld.append(current_key)
                if current_value.startswith("catalog#"):
                    current_value = current_value.replace("catalog#, or reference):", "").strip()
                return current_value
        return None


    for k, v in description_dict.items():
        if not (k and v):
            continue

        if not vendor:
            vendor = if_match_then_get("vendor", k)

        if not cat:
            cat = if_match_then_get("catalog", k)

        if not lot:
            lot = if_match_then_get("lot", k)

    print (vendor, cat, lot, target)
    if vendor:
        name_list.append(vendor)

    if cat:
        name_list.append(cat)

    if lot:
        name_list.append(lot)

    if not vendor and not cat and not lot:
        if target:
            name_list.append(target)


    name = ", ".join(name_list)
    #3. try to get the antibody
    if name:
        ret, created = models.Antibodies.objects.get_or_create(name=name)
        return ret
    else:
        return None


def parseFactorByAntibody(geoPost):
    targetFlds = ["CHIP_ANTIBODY", "ANTIBODY", "CHIP", "ANTIBODY_SOURCE", "ANTIBODY_ANTIBODYDESCRIPTION",
                  "ANTIBODY_TARGETDESCRIPTION"]
    #1. try to get the values
    for t in targetFlds:
        tmp = getFromPost(geoPost, t).strip()
        if not tmp:
            continue
        tmp = tmp.upper().replace("ANTI-", " ").replace("ANTI", " ").strip()
        if len(tmp) < 10 and tmp != "":
            return models.Factors.objects.get_or_create(name=tmp)[0]

        splited = re.findall(r"[\w-]+", tmp)
        for s in splited:

            if re.match(r"^[\d-]+$", s):
                continue

            if d.check(s):
                continue

            if s.startswith("POL2") and len(s) < 10:
                return models.Factors.objects.get_or_create(name=tmp)[0]

            if models.Factors.objects.filter(name__iexact=s):
                return models.Factors.objects.get(name__iexact=s)
        if "INPUT" in splited:
            return models.Factors.objects.get_or_create(name="Input")[0]
        if ("POLYMERASE" in splited) or ("POL" in splited):
            return models.Factors.objects.get_or_create(name="POL2")[0]

    return None


def createSample(gsmid, overwrite=False):
    """Given a gsmid, tries to create a new sample--auto-filling in the
    meta fields


    If overwrite is True and there is the sample that has the same gsmid, this function will overwrite that sample

    NOTE: will try to save the sample!!

    Returns newly created sample
    """
    #dynamically load classifiers


    # if not hasattr(_this_mod, "classifiers"):
    #     classifiers = __import__("classifiers", globals(), locals(), ["*"], -1)
    #     setattr(_this_mod, "classifiers", classifiers)
    # else:
    #     classifiers = getattr(_this_mod, "classifiers")

    # sraId = gsmToSra(gsmid)
    # sraXML = sra.getSraXML(sraId) if sraId else None
    # geoPost = postProcessGeo(gsmid)
    # gseId = gsmToGse(gsmid)
    # pmid = gseToPubmed(gseId) if gseId else None
    #print geoPost

    if not overwrite:
        s = models.Samples()
        s.status = "new"
        s.unique_id = gsmid
    else:
        s, created = models.Samples.objects.get_or_create(unique_id=gsmid)
        if created:
            s.status = "new"

    # #add the other ids-
    # idList = {'sra': sraId, 'gse': gseId, 'pmid': pmid}
    # s.other_ids = json.dumps(idList)
    #
    # if pmid:
    #     s.paper = pubmed.getOrCreatePaper(pmid)
    #
    # s.name = getFromPost(geoPost, "title")
    # s.date_collected = datetime.datetime.now()
    # s.fastq_file_url = sra.getSRA_downloadLink(sraXML) if sraXML else None
    #
    # if getFromPost(geoPost, "organism") == "HOMO SAPIENS":
    #     s.species = models.Species.objects.get(pk=1)
    # else:
    #     s.species = models.Species.objects.get(pk=2)



    #HERE is where I need to create a classifier app/module
    #FACTOR, platform, species--HERE are the rest of them!
    fields = ['factor', 'cell_type', 'cell_line', 'cell_pop', 'strain',
              'disease_state', 'tissue_type']
    _map = {'factor': models.Factors, 'cell_type': models.CellTypes,
            'cell_line': models.CellLines,
            'cell_pop': models.CellPops, 'strain': models.Strains,
            'disease_state': models.DiseaseStates,
            'tissue_type': models.TissueTypes}

    description_dict = parseGeoInfo(gsmid)
    s.description = json.dumps(description_dict)
    # for f in fields:
    #     tmp = classifiers.classify(getattr(classifiers, f), geoPost)[0]
    #     #IS it above the threshold?
    #     if tmp[0] > 0.65:
    #         #try to find the field
    #         fld = _map[f].objects.filter(name__icontains=tmp[1])
    #         if fld:
    #             setattr(s, f, fld[0])

    s.antibody = parseAntibody(description_dict)
    print gsmid
    print s.antibody

    #fields.extend(['name', 'date_collected', 'fastq_file_url', "unique_id",
    #               "status", "species"])
    #for f in fields:
    #    print getattr(s, f)
    # try:
    #     if not s.factor and "input" in s.name.lower():
    #         s.factor = models.Factors.objects.get(name="Input")
    # except:
    #     print s
    #     raise
    ## For faster

    # if not s.factor:
    #     s.factor = parseFactorByAntibody(geoPost)

    try:
        if not s.cell_type and "cell type" in description_dict:
            s.cell_type, created = models.CellTypes.objects.get_or_create(name=description_dict['cell type'])
            if created:
                s.cell_type.status = "new"

        if not s.cell_line and "cell line" in description_dict:
            if len(description_dict['cell line']) < 255:
                s.cell_line, created = models.CellLines.objects.get_or_create(name=description_dict['cell line'])
                if created:
                    s.cell_line.status = "new"

        if not s.tissue_type and "tissue" in description_dict:
            s.tissue_type, created = models.TissueTypes.objects.get_or_create(name=description_dict['tissue'])
            if created:
                s.tissue_type.status = "new"

        if not s.strain and 'strain' in description_dict:
            s.strain, created = models.Strains.objects.get_or_create(name=description_dict['strain'])
            if created:
                s.strain.status = "new"
    except:
        print description_dict
        print "continue"
        return s

    s.save()
    return s


def updateSamples():
    """Will run through the whole flow of this package, trying to update
    the db w/ new samples if any.

    Returns: list of newly created samples
    """
    print "1. refresh the repository"
    #    gdsSamples = getGDSSamples()
    #    for gdsid in gdsSamples:
    #        gsm = gsm_idToAcc(gdsid)
    #        if gsm:
    #            geoXML = getGeoXML(gsm)
    #            geoPost = postProcessGeo(gsm)
    #
    #            #"2a. sync geo and sra"
    #            sraId = gsmToSra(gsm)
    #            if sraId:
    #                sra.getSraXML(sraId)

    print "2. get the chip-seq samples"
    samples = getGeoSamples_byType("geo", "ChIP-Seq", refresh=True)
    #samples = getGeoSamples_byType()

    print "#3. try to create new samples"
    cnt_changed = 0
    ret = []
    for s in samples:
        samples_have_same_id = models.Samples.objects.filter(unique_id=s)

        if samples_have_same_id.exists():
            if samples_have_same_id[0].status == "new":
                # Avoid changing old samples. Only update new-parsed samples.
                tmp = createSample(s, overwrite=True)
                print "overwrite", s
            else:
                print s, "already exist"
                continue
        else:
            # when the gsmid has never been parsed before
            print s, "new sample"
            tmp = createSample(s)

        cnt_changed += 1
        ret.append(tmp)
        #stop after creating 10
        # if cnt_changed == 10:
        #    sys.exit()
    return ret
