from django.core.management import setup_environ
import sys
sys.path.insert(0,'/data1/newdc1.4/src')
import settings
setup_environ(settings) 
from datacollection import models
from datacollection.models import Factors
#from django.core.exceptions import DoesNotExist


factors = models.Factors.objects.all()
dic = {}
for line in open('/data1/home/chenfei/shared_users/wuqiu/newdc/files/factor_type.txt','r'):
	line = line.strip().split('\t')
	factor_name = line[0]
	factor_type = line[1]
	for i in factors:
		if i.name in factor_name:
			i.type = factor_type
			i.save()
		else:
			continue

		
			
	
