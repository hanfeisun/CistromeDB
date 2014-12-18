from django.core.management import setup_environ
import sys
sys.path.insert(0,'/data1/newdc1.4/src')
import settings
setup_environ(settings) 
from datacollection import models

dic = {}
for line in open('/data1/home/chenfei/shared_users/wuqiu/newdc/files/journal_IF.txt','r'):
	line = line.strip().split('\t')
	journal_name = line[0]
	journal_IF = float(line[1])
	dic[journal_name] = journal_IF	
	current_journal = models.Journals.objects.get(name=journal_name)
	current_journal.impact_factor = journal_IF
	current_journal.save()
	
	
