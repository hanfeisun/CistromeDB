from django.core.management import setup_environ
import sys
sys.path.insert(0,'/data1/newdc1.4/src')
import settings
setup_environ(settings) 

#load the django model
from datacollection import models
from datacollection.models import CellLines
from datacollection.models import CellTypes
from datacollection.models import TissueTypes
from datacollection.models import CellPops
from datacollection.models import Strains

celllines = models.CellLines.objects.all()
celltypes = models.CellTypes.objects.all()
tissuetypes = models.TissueTypes.objects.all()
cellpops = models.CellPops.objects.all()
strains = models.Strains.objects.all()

def upper_name(name):
	'''The alternative options of name: 
	celllines, celltypes, tissuetypes and cellpops, strains'''
	name_upper = []
	for row in name:
		name_upper.append(row.__str__().upper())
	return name_upper
	
cellview_upper = []
cellview_upper = upper_name(celllines) + upper_name(celltypes) + upper_name(tissuetypes) + upper_name(cellpops) + upper_name(strains)

print cellview_upper

#find the redundancy
def redundancy(name_upper):
	'''The alternative options of name: cellview_upper'''
	dit = {}
	t = 0
	for i in name_upper:
		dit[i] = dit.get(i, 0) + 1
	w1 = open('/data1/home/chenfei/shared_users/wuqiu/newdc/files/cell_redundancy.txt', 'w')
	for k, v in dit.iteritems():
        	if v > 1:
                	print >>w1, k,v
                	t += 1
	if t == 0:
        	print >>w1, 'No redundancy!'
	w1.close()

redundancy(cellview_upper)
#print redundancy.__doc__




