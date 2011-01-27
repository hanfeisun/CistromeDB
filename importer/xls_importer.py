"""
Synopsis: given a tab-delimited representation of the tongji xls file,
this script tries to import all of the papers into the newdc db
"""

import sys
import time
import re
import httplib
import urllib, urllib2

def main():
    txt_filename = "stat.txt"
    max_papers = 50 #set a max number of papers to import, or set to -1 for all
    gse_pattern = re.compile(r"GSE\d{5}")

    #grab GSEIDs from the file
    gseids = []
    
    f = open(txt_filename)

    line = f.readline()
    f.close()
    #NOTE: i can't get dos2unix to work; it's read as one big line...blame MSFT
    tokens = line.split() #each thing will be a token
    for t in tokens:
        if gse_pattern.match(t) and not (t in gseids):
            gseids.append(t)

    if max_papers >= 0:
        m = max_papers
    else:
        m = len(gseids)

    #LOGIN- ref: http://personalpages.tds.net/~kent37/kk/00010.html
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    urllib2.install_opener(opener)
    params = urllib.urlencode(dict(username='lentaing', password='lentaing'))
    f = opener.open('http://localhost:8000/accounts/login/', params)
    data = f.read()
    f.close()

    #now feed these into the autoimporter
    papers_added = []
    for i in range(m):
        try:
            params = urllib.urlencode(dict(gseid=gseids[i], json="true"))
            f = urllib2.urlopen('http://localhost:8000/auto_paper_import/',
                                params)
            data = f.read()
            f.close()
            if data.find("true") > 0:
                papers_added.append(gseids[i])
            #wait 1 second between posts
            time.sleep(1)
        except:
            print sys.exc_info()[0]

    f = open("papers_added.txt","w")
    for p  in papers_added:
        f.write("%s\n" % p)
    f.close()
            

if __name__ == "__main__":
    main()
