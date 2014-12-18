from django.core.management import setup_environ
import sys
sys.path.insert(0,'/data/newdc1.4/src')
import settings
setup_environ(settings) 
from datacollection import models
from datacollection.models import Factors

factors = models.Factors.objects.all()

print "\t".join(["Factor","Type","Status"])

for i in factors:
	if i.status == "ok":
		print i.name, \
			"\t", \
			i.type, \
			"\t", \
			i.status, \
			"\n",
	else:
		continue
		
