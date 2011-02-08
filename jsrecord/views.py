import sys

from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response

from django.core import serializers
from django.db.models.base import ModelBase
from django.forms import ModelForm
from django.db import models

from new import classobj
from datetime import date, datetime
from django.db.models.fields.files import FieldFile
import django.db.models.fields as fields
from types import *

from django.db.models import get_app

#NOTE: the following can be defined in a 'jsrecord.settings.py'--just like
#how settings.py lets you define which db table to access, here were can define
#which app models to expose.
#
#02-07-11 Follow up: we should have router take in a different param called
#app!  THEN jsrecord will truly be plug and play for any project!
MODELS = get_app('datacollection')

#dynamically build their forms and map them
#NOTE: we use _MODELFORMS to validate the fields in Save, but that's alot of
#lines for something that is easy...maybe i should redo this
_MODELFORMS = {}
MODEL_TYPES = []

#a trick to get the current module
_modname = globals()['__name__']
_this_mod = sys.modules[_modname]

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
    #REFACTORING
    tmp = [jsonify(o) for o in model.objects.all()]    
    return HttpResponse("[%s]" % ",".join(tmp))

    #return HttpResponse("[]")
#     list = model.objects.all()

#     tmp = ""
#     if (list.__len__() > 0):
#         tmp += jsonify(list[0])
#         for i in range(1, list.__len__()):
#             tmp += ","+jsonify(list[i])
        
#     return HttpResponse("["+tmp+"]")

def Get(request, model, id):
    m = model.objects.get(pk=id)
    return HttpResponse(jsonify(m))

def Find(request, model, options):
    #we need to do this b/c request.GET is an invalid dict to pass in
    opts = dict([(str(x),request.GET[x]) for x in request.GET.keys()])
    tmp = [jsonify(o) for o in model.objects.filter(**opts)]
    #print tmp
    return HttpResponse("[%s]" % ",".join(tmp))
    
    #REFACTORING
#    list = model.objects.filter(**opts)
#    tmp = ""
#    if (list.__len__() > 0):
#         tmp += jsonify(list[0])
#     for i in range(1, list.__len__()):
#         tmp += ","+jsonify(list[i])

#     return HttpResponse('(['+tmp+'])')

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
            return HttpResponse('{\"success\":true, \"obj\":'+jsonify(new_m)+'}')
        else:
            return HttpResponse('{\"success\":false, \"err\":\"%s\"}' % form.errors) 

def Delete(request, _model, id):
    """Given a django model and an id, tries to delete the record from the db
    """
    try:
        tmp = _model.objects.get(pk=id)
        if tmp:
            tmp.delete()
            return HttpResponse('{\"success\":true}')
        else:
            return HttpResponse('{\"success\":false}')
    except Exception:
        return HttpResponse("{\"success\":false, \"err\":\"%s:%s\"}" %
                            (sys.exc_type, sys.exc_value))

def loader(request, model):
    """Given a django model as a url param, this returns the meta information
    so that an equivalent javascript class can be constructed"""
    _model = getattr(MODELS, model)
    fields = [field.name for field in _model._meta.fields]
    tmp = "{\"className\":%s, \"fields\":%s}" % (json.dumps(_model.__name__),
                                                 json.dumps(fields))
    return HttpResponse(tmp)

def router(request, model, verb, rest):
    """routes the verb to the appropriate function, e.g.
    all --> All, get --> 'Get, etc.
    maybe i should refactor this...
    """
    _model = getattr(MODELS, model)
    two_param = ["all", "save"]
    three_param = ["get", "find", "delete"]
    if verb in two_param:
        return getattr(_this_mod, verb.capitalize())(request, _model)
    elif verb in three_param:
        return getattr(_this_mod, verb.capitalize())(request, _model, rest)
    else:
        return HttpResponse("{\"err\":\"invalid verb\"}")
    #REFACTORING
#     if verb == "all":
#         return All(request, _model)
#     elif verb == "get":
#         return Get(request, _model, rest)
#     elif verb == "find":
#         return Find(request, _model, rest)
#     elif verb == "save":
#         return Save(request, _model)
#     elif verb == "delete":
#         return Delete(request, _model, rest)
    
    
#REFACTORING: moving to use the std json module instead.
# def serializeField(obj, fieldName):
#     val = getattr(obj, fieldName)
    
#     if val == 0:
#         return "\"%s\":0" % fieldName
#     if not val or type(val) is NoneType:
#         return "\"%s\":null" % fieldName
#     elif type(val) in MODEL_TYPES: #its a django model, return the id
#         return "\"%s\":%s" % (fieldName, str(val.id))
#     elif type(val) is StringType or type(val) is UnicodeType:
#         return "\"%s\":\"%s\"" % (fieldName, val)
#     elif type(val) is date or type(val) is datetime or type(val) is FieldFile:
#         return "\"%s\":\"%s\"" % (fieldName, str(val))
#     elif isinstance(val, models.Model):
#         return "\"%s\":\"%s\"" % (fieldName, str(val))
#     elif type(val) is type(True): #bool type
#         if val:
#             return "\"%s\":true" % fieldName
#         else:
#             return "\"%s\":false" % fieldName
#     else:
#         return "\"%s\":%s" % (fieldName, str(val))

# def jsonify(modelObj):
#     json = "{"
#     fields = modelObj._meta.fields
#     if (fields.__len__() > 0):
#         json += serializeField(modelObj, fields[0].name)
#     for i in range(1, fields.__len__()):
#         json += ", "+serializeField(modelObj, fields[i].name)

#     return json+"}"

class ModelEncoder(json.JSONEncoder):
    """Override the default method to try to dump Models as json"""
    @staticmethod
    def _modelAsDict(modelObj):
        """We need this b/c we need to walk down the tree and make records
        all along before dumping it as a tring"""
        tmp = {"_class":modelObj.__class__.__name__}
        for f in modelObj._meta.fields:
            val = getattr(modelObj, f.name)
            if isinstance(val, models.Model):
                val = ModelEncoder._modelAsDict(val)
            if isinstance(val, FieldFile) or isinstance(val, date) or \
                   isinstance(val, datetime):
                val = str(val)
            tmp[f.name] = val
        return tmp
    
    def default(self, obj):
        if isinstance(obj, models.Model):
            return json.dumps(ModelEncoder._modelAsDict(obj))
        return json.JSONEncoder.default(self, obj)


def jsonify(modelObj):
    """Serializes the django model object"""
    #NOTE: i can't get the cls kwarg to work for json.dumps, it gives me a
    #bug- it dumps models as STRINGS and not as json records, e.g.
    # "{\"_class\": \"TestModelA\", \"id\": null, \"foo\": \"some string\"}"
    # rather than:
    # {"_class": "TestModelA", "id": null, "foo": "some string"}

    tmp = ModelEncoder._modelAsDict(modelObj)
    return json.dumps(tmp)
