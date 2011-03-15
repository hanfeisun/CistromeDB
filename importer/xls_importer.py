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
                "Chenyang Wang": "chenyangwang",
                "Xikun Duan": "xinkunduan",
                "Hongtao Sun": "hongtaosun",
                "Qixuan Wang": "qixuanwang",
                "Bo Qin": "boqin",
                "Haiyang Zheng": "haiyangzheng",
                }

    gsm_pattern = "^GSM\d{6}$"
    #another pass through the data
    not_processed = []
    for (i, e) in enumerate(entries):
        #try to get the paper associated with the dataset
        try:
            p = models.Papers.objects.filter(gseid=e['GSEID'])
            if not p:
                #need to create a new paper
                username = userDict[e['Student Name']]
                if username:
                    user = User.objects.filter(username=username)[0]
                else:
                    #default to lentaing/shirleyliu
                    user = User.objects.get(pk=1)
                #create the paper
                p = views._import_paper(e['GSEID'], user)
                #import the datasets
                geoQuery = entrez.PaperAdapter(p.gseid)
                views._auto_dataset_import(p, user, geoQuery.datasets)
        except:
            print "Exception in user code:"
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60
            not_processed.append(i)
            #sys.exit(-1)

    f = open("not_processed.txt", "w")
    for n in not_processed:
        f.write(n)
    f.close()
    
if __name__ == "__main__":
    main()
