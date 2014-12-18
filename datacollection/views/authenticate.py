import json as json
from django.http import HttpResponse

__author__ = 'hanfei'


def check_authenticated(request):
    if not request.user.is_authenticated():
        return HttpResponse(json.dumps({"status": "logout"}))
    else:
        return HttpResponse(
            json.dumps({"status": "login", "username": request.user.username}), mimetype='application/json')