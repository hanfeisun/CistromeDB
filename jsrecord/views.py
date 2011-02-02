import sys

from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response

from django.core import serializers
from django.db.models.base import ModelBase
from django.forms import ModelForm

from new import classobj
from datetime import date, datetime
from django.db.models.fields.files import FieldFile
from types import *

from django.db.models import get_app

#NOTE: the following can be defined in a 'jsrecord.settings.py'--just like
#how settings.py lets you define which db table to access, here were can define
#which app models to expose.
MODELS = get_app('datacollection')

#dynamically build their forms and map them
_MODELFORMS = {}
MODEL_TYPES = []

try:
    import json
except ImportError:
    import simplejson as json

#awesome, i can create class objects programmatically!
for m in dir(MODELS):
    model = getattr(MODELS,m)
    if type(model) is ModelBase: #create a form
        MODEL_TYPES.append(model) #add model to the list of MODELS
        tmp = classobj(m+'Form', (ModelForm,),
                       {'Meta': classobj('Meta',(),{'model':model})})
        _MODELFORMS[model] = tmp

def All(request, model):
    list = model.objects.all()

    tmp = ""
    if (list.__len__() > 0):
        tmp += jsonify(list[0])
        for i in range(1, list.__len__()):
            tmp += ","+jsonify(list[i])
        
    return HttpResponse("(["+tmp+"])")

def Get(request, model, id):
    m = model.objects.get(pk=id)
    return HttpResponse("("+jsonify(m)+")")

def Find(request, model, options):
    #we need to do this b/c request.GET is an invalid dict to pass in
    opts = dict([(str(x),request.GET[x]) for x in request.GET.keys()]) 
    list = model.objects.filter(**opts)
    tmp = ""
    if (list.__len__() > 0):
        tmp += jsonify(list[0])
    for i in range(1, list.__len__()):
        tmp += ","+jsonify(list[i])

    return HttpResponse('(['+tmp+'])')

def Save(request, model):
    if request.method == 'POST':
#        print request.POST
        if request.POST['id'] and request.POST['id'] != "null":
            s = model.objects.get(pk=request.POST['id'])
        else:
            s = None

        form = _MODELFORMS[model](request.POST, instance=s)
        if form.is_valid():
            new_m = form.save()
            return HttpResponse('({success:true, obj:'+jsonify(new_m)+'})')
        else:
            return HttpResponse('({success:false, err:\"%s\"})' % form.errors) 

def Delete(request, _model, id):
    try:
        tmp = _model.objects.get(pk=id)
        if tmp:
            tmp.delete()
            return HttpResponse('({success:true})')
        else:
            return HttpResponse('({success:false})')
    except Exception:
        return HttpResponse("({success:false, err:\"%s:%s\"})" %
                            (sys.exc_type, sys.exc_value))

def loader(request, model):
    _model = getattr(MODELS, model)
    fields = [field.name for field in _model._meta.fields]
    json = "({className:\""+_model.__name__+"\", fields:"+str(fields)+"})"
    return HttpResponse(json)

def router(request, model, verb, rest):
    _model = getattr(MODELS, model)
    if verb == "all":
        return All(request, _model)
    elif verb == "get":
        return Get(request, _model, rest)
    elif verb == "find":
        return Find(request, _model, rest)
    elif verb == "save":
        return Save(request, _model)
    elif verb == "delete":
        return Delete(request, _model, rest)

def serializeField(obj, fieldName):
    val = getattr(obj, fieldName)
    if val == 0:
        return fieldName+":0"
    if not val or type(val) is NoneType:
        return fieldName+":null"
    elif type(val) in MODEL_TYPES: #its a django model, return the id
        return fieldName+":"+str(val.id)
    elif type(val) is StringType or type(val) is UnicodeType:
        return fieldName+":\""+val+"\""
    elif type(val) is date or type(val) is datetime or type(val) is FieldFile:
        return fieldName+":\""+str(val)+"\""
    else:
        return fieldName+":"+str(val)

def jsonify(modelObj):
    json = "{"
    fields = modelObj._meta.fields
    if (fields.__len__() > 0):
        json += serializeField(modelObj, fields[0].name)
    for i in range(1, fields.__len__()):
        json += ", "+serializeField(modelObj, fields[i].name)

    return json+"}"

