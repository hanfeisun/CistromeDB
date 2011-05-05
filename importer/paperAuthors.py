#!/usr/bin/python
"""
SYNOPSIS: previous to 2011-05-05, paper authors were being set to the list
defined by GEO.  It should actually come from PUBMED.  This simple script
corrects that error.
"""
import sys
import traceback

#NOTE: pip depends on import_settings to define NEWDC_DIR
import importer_settings
sys.path.insert(0, importer_settings.DEPLOY_DIR)

from django.core.management import setup_environ
import settings

setup_environ(settings)

from datacollection import models
from entrezutils import models as emodels

USAGE = "usage: %prog"

def main():
    """
    For every paper entry, replaces the authors field w/ EntrezAuthor
    """
    papers = models.Papers.objects.all()
    changed = []
    for p in papers:
        pubmed = emodels.PubmedSummary(p.pmid)
        auths = ",".join(pubmed.authors)
        if p.authors != auths:
            try:
                changed.append(p.id)
                p.authors = auths
                p.save()
            except:
                print "Exception in user code:"
                print "%s\n%s\n%s" % (p.id, len(auths), p.authors)
                print '-'*60
                traceback.print_exc(file=sys.stdout)
                print '-'*60


    f = open("paperAuthorChangeList.txt", "w")
    for i in changed:
        f.write("%s\n" % i)
    f.close()

if __name__ == "__main__":
    main()
        
