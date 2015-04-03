#../bin/python manage.py dumpdata --natural --exclude contenttypes -e sessions -e admin -e auth --exclude auth.permission --exclude corsheaders --indent=4 -v 2 --traceback > dc.json
../bin/python manage.py sqlflush > schema.sql
