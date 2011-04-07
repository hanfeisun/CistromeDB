#!/usr/bin/env python
"""
Synopsis: Given a xls(x) file filled with dc dataset information, try to
import the data into the newdc using autoimport fns

NOTE: this is a major rewrite of the original xls importer b/c now we
1. rely on the openpyxl package to read in xls files, and
2. we are not going through the web to create the datasets, but will
do it all in django
"""
import os
import sys
import optparse
import traceback
import re

import importer_settings
sys.path.insert(0,importer_settings.DEPLOY_DIR)
from django.core.management import setup_environ
import settings
setup_environ(settings)
from datacollection import models
from datacollection import views
from django.contrib.auth.models import User
from entrezutils import models as entrez

from openpyxl.reader.excel import load_workbook

USAGE = """USAGE: xls_importer.py -f foo.xlsx
Parameters:
         -f - the xls file to import
"""


def main():
    parser = optparse.OptionParser(usage=USAGE)
    parser.add_option("-f", "--file",
                      help="path to the dir which to search for packages")
    (opts, args) = parser.parse_args(sys.argv)
    if not opts.file:
        print USAGE
        sys.exit(-1)

    if not os.path.exists(opts.file):
        print "File does not exist"
        sys.exit(-1)

    #try to load the workbook:
    wb = load_workbook(opts.file)
    sheet = wb.get_active_sheet()

    #load the data into a list of dictionaries
    cols = []
    entries = []
    for (i,r) in enumerate(sheet.rows):
        if i == 0:
            #the first row defines the columns
            cols = [c.value for c in r]
        else:
            tmp = {}
            for (key, cell) in zip(cols, r):
                tmp.__setitem__(key, cell.value)
            entries.append(tmp)

    #maps xls student names to dc usernames
        #users = User.objects.all()
    userDict = {"Xueqiu Lin":"xueqiulin",
                "Ying Ge": "yingge",
                "Hanfei Sun": "hanfeisun",
                "Su Wang": "suwang",
                "Luying Wang": "luyingwang",
                "Mingyang Wang": "mingyangwang",
                "Chengyang Wang": "chengyangwang",
                "Xikun Duan": "xikunduan",
                "Hongtao Sun": "hongtaosun",
                "Qixuan Wang": "qixuanwang",
                "Bo Qin": "boqin",
                "Haiyang Zheng": "haiyangzheng",
                "Chenfei Wang": "chenfeiwang",
                "JunshengChen": "junshengchen",
                }

    gse_pattern = "^GSE\d{5}$"
    #another pass through the data
    not_processed = []
    #we only want to import AB and Illumina platforms
    ok_platforms = ['GPL9185', 'GPL7139', 'GPL6333', 'GPL6103', #illumina mm
                    'GPL9052', 'GPL9115', 'GPL10999', #illumina hs
                    'GPL9138', 'GPL10279', 'GPL9318', 'GPL10010'] #AB
    for (i, e) in enumerate(entries):
        #try to get the paper associated with the dataset
        try:
            gseid = e['GSEID'].strip()
            if re.match(gse_pattern, gseid):
                p = models.Papers.objects.filter(gseid=gseid)
                if not p:
                    #need to create a new paper
                    username = userDict[e['Student Name'].strip()]
                    if username:
                        user = User.objects.filter(username=username)[0]
                    else:
                        #default to lentaing/shirleyliu
                        user = User.objects.get(pk=1)
                    gplid = e['Platform ID'].strip()
                    if gplid in ok_platforms:
                        #create the paper
                        p = views._import_paper(gseid, user)
                        #import the datasets
                        geoQuery = entrez.PaperAdapter(p.gseid)
                        views._auto_dataset_import(p, user, geoQuery.datasets)
                    else:
                        if gseid not in not_processed:
                            not_processed.append(gseid)
            else:
                if gseid not in not_processed:
                    not_processed.append(gseid)
        except:
            print "Exception in user code: " 
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
            if e['GSEID'].strip() not in not_processed:
                not_processed.append(e['GSEID'])
            print "GSEID: %s" % e['GSEID']
            print "User: %s" % e['Student Name']
            #sys.exit(-1)

    f = open("not_processed.txt", "w")
    for n in not_processed:
        f.write("%s\n" % n)
    f.close()
    
if __name__ == "__main__":
    main()
