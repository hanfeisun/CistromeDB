from django.core.management import setup_environ
import sys

sys.path.insert(0, '/data1/newdc1.4/src')
import settings

setup_environ(settings)
from datacollection import models
# from django.core.exceptions import ObjectDoesNotExist

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

w1 = open('/data1/home/chenfei/shared_users/wuqiu/newdc/files/celltypes.txt', 'w')
w2 = open('/data1/home/chenfei/shared_users/wuqiu/newdc/files/tissuetypes.txt', 'w')

# for i in factors:
#         if i.id <= 476:
#                 print >> w1, i.id, i.name 

for i in celltypes:
	print >> w1, i.id, i.name 

for i in tissuetypes:
	print >> w2, i.id, i.name 
                
w1.close()
w2.close()



# factors = models.Factors.objects.all()
# dic = {}
# for line in open('/data1/home/chenfei/shared_users/wuqiu/alias_list.txt', 'r'):
#     line = line.strip().split('\t')
#     if len(line) != 2:
#         continue
#     factor_name = line[0]
#     alias_names = line[1].strip().split(", ")
# 
#     if alias_names:
#         dic[factor_name] = alias_names
#         try:
#             current_factor = models.Factors.objects.get(name=factor_name)
#         except ObjectDoesNotExist:
#             continue
#     else:
#         continue
#     if not current_factor:
#         continue
#     for a in alias_names:
#         '''try:'''
#         a1, created = models.Aliases.objects.get_or_create(name=a, factor=current_factor)
#         '''except:
#             print current_factor
#             print a
#             raise'''
#         '''print a1'''
#         a1.save()


