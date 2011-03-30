#!/usr/bin/env python
"""
Synopsis: Given a xls(x) file filled with dc dataset information, try to
import the data into the newdc using autoimport fns

xls_info, just tries to use the autoimport fn but it doesn't import things
like factor, tissue type, etc.  so this program tries to fill in the gap.
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
            
    #note we assume that xls_importer has alread been run; so all we need to
    #do is to add the associated info
    gsm_pattern = "^GSM\d{6}$"
    #another pass through the data
    processed = []
    not_processed = []
    for (i, e) in enumerate(entries):
        #try to get the associated dataset
        d = None
        gsmid = e['ChIP GSMID']
        if (re.match(gsm_pattern, gsmid)):
            d = models.Datasets.objects.filter(gsmid=e['ChIP GSMID'])
        if d:
            #d is a queryset, we have to get the first item--which is a 
            #dataset model obj
            d = d[0] 
            #(d.factor, created) = \
            #           models.Factors.objects.get_or_create(name=e['Factor'])
            factor = None
            try:
                f = e['Factor']
                a = e['Antibody']
                if f and a:
                    factor = models.Factors.objects.get(name=f.strip(), 
                                                        antibody=a.strip())
                elif f:
                    factor = models.Factors.objects.get(name=f.strip())
            except: #factor not found
                pass
            
            if not factor:
                #create a new factor
                f = e['Factor']
                a = e['Antibody']
                factor = models.Factors()
                factor.name = f.strip() if f else ""
                factor.antibody = a.strip() if a else ""
                factor.save()
                
            d.factor = factor
            #experiment type here?!

            cell_type = None
            try:
                ct = e['Cell Type']
                tt = e['Tissue Type']
                if ct and tt:
                    cell_type = models.CellTypes.objects.get(name=ct.strip(),
                                                             tissue_type=tt.strip())
                elif ct:
                    cell_type = models.CellTypes.objects.get(name=ct.strip())
            except: #cell_type
                pass
            if not cell_type:
                #create a new cell type
                ct = e['Cell Type']
                tt = e['Tissue Type']
                cell_type = models.CellTypes()
                cell_type.name= ct.strip() if ct else ""
                cell_type.tissue_type= tt.strip() if tt else ""
                cell_type.save()
            d.cell_type = cell_type

            cl = e['Cell Line']
            if cl:
                try:
                    (cell_line, created) = models.CellLines.objects.get_or_create(name=cl.strip())
                    d.cell_line = cell_line
                except:
                    pass

            cp = e['Cell Population']
            if cp:
                try:
                    (cell_pop, created) = models.CellPops.objects.get_or_create(name=cp.strip())
                    d.cell_pop = cell_pop
                except:
                    pass

            s = e['Strain and mutation']
            if s:
                try:
                    (strain, created) = models.Strains.objects.get_or_create(name=s.strip())
                    d.strain = strain
                except:
                    pass

            #disease state here!
            ds = e['Disease state']
            if ds:
                try:
                    (disease_state, created) = models.DiseaseStates.objects.get_or_create(name=ds.strip())
                    d.disease_state = disease_state
                except:
                    pass

            cnd = e['Condition']
            if cnd:
                try:
                    (condition, created) = models.Conditions.objects.get_or_create(name=cnd.strip())
                    d.condition = condition
                except:
                    pass

            chip_page = e['ChIP page']
            if chip_page:
                d.chip_page = chip_page.strip()

            control_gsmid = e['Control GSMID']
            if control_gsmid and re.match(gsm_pattern, control_gsmid.strip()):
                d.control_gsmid = control_gsmid.strip()

            control_page = e['Control page']
            if control_page:
                d.control_page = control_page.strip()

            #save here
            #processed.append(e['ChIP GSMID'])
            d.save()
        else:
            not_processed.append(e['ChIP GSMID'])

    f = open("not_processed.txt", "w")
    for n in not_processed:
        f.write("%s\n" % n)
    f.close()
    
if __name__ == "__main__":
    main()
