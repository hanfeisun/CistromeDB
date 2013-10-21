from django.core.management import setup_environ
import sys
sys.path.insert(0,'/Users/wuwuqiu/Desktop/Projects/cistrome/database/newdc')
import settings
setup_environ(settings) 
from datacollection import models
from django.core.exceptions import ObjectDoesNotExist



'''w1 = open('/data1/home/chenfei/wuqiu/factor.txt', 'w')
factors = models.Factors.objects.all()
for i in factors:
        if i.id <= 476:
                print >> w1, i.id, i.name 
w1.close()'''

factors = models.Factors.objects.all()
dic = {}
for line in open('/Users/wuwuqiu/Desktop/Projects/cistrome/database/newdc/scripts/alias_list.txt','r'):
	line = line.strip().split('\t')
	if len(line) != 2:
		continue
	factor_name = line[0]
	alias_names = line[1].strip().split(", ")

	if alias_names:
		dic[factor_name] = alias_names
		try:
			current_factor = models.Factors.objects.get(name=factor_name)
		except ObjectDoesNotExist:
			continue
	else:
		continue
	if not current_factor:
		continue
	for a in alias_names:
		'''try:'''
		a1,created = models.Aliases.objects.get_or_create(name = a, factor = current_factor)
		'''except:
			print current_factor
			print a
			raise'''
		'''print a1'''
		a1.save()


