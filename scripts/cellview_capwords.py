from django.core.management import setup_environ
import sys
sys.path.insert(0,'/data1/newdc1.4/src')
import settings
import string
import re
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

#from django.core.exceptions import DoesNotExist

# w1 = open('/Users/wuwuqiu/Desktop/Projects/cistrome/database/newdc/celltypes.txt', 'w')
# w2 = open('/Users/wuwuqiu/Desktop/Projects/cistrome/database/newdc/tissuetypes.txt', 'w')

'''for i in celltypes:
	# print >> w1, i.id, i.name
	i.name = string.capwords(i.name)
	strinfo = re.compile('Cells')
	i.name = strinfo.sub('Cell',i.name)
	i.save()
for j in tissuetypes:
	# print >> w2, i.id, i.name
	j.name = string.capwords(j.name)
	j.save()'''

for a in celllines:
	cl_sample = models.CellLines.objects.get(name=a.name).cl_samples.all()
	if cl_sample:
		continue
	else:
		a.delete()
		print a.name
# 		del a.name
# 	a.save()
for b in celltypes:
	ct_sample = models.CellTypes.objects.get(name=b.name).ct_samples.all()
	if ct_sample:
		continue
	else:
		b.delete()
		print b.name
		
		
for c in cellpops:
	cp_sample = models.CellPops.objects.get(name=c.name).cp_samples.all()
	if cp_sample:
		continue
	else:
		c.delete()
		print c.name
		
for d in tissuetypes:
	tt_sample = models.TissueTypes.objects.get(name=d.name).tt_samples.all()
	if tt_sample:
		continue
	else:
		d.delete()
		print d.name


# ct_sample = models.CellTypes.objects.get(name=b.name).ct_samples.all()
# cp_sample = models.CellPops.objects.get(name=c.name).cp_samples.all()
# tt_sample = models.TissueTypes.objects.get(name=d.name).tt_samples.all()





	
# w1.close()
# w2.close()

	
	
	# if i.name in factor_name:
# 		i.type = factor_type
# 		i.save()
# 	else:
# 		continue

		
			
	
