import sys

from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response

from django.core import serializers
from django.db.models.base import ModelBase
from django.forms import ModelForm
from django.db import models
from django.views.decorators.cache import cache_page

from new import classobj
from datetime import date, datetime
from django.db.models.fields.files import FieldFile
from django.db.models.fields.related import ManyToManyField
import django.db.models.fields.related as related
#import django.db.models.fields.related.ManyRelatedManager as ManyRelatedManager
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

#timeout = 15 mins
_timeout = 60*15

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

@cache_page(_timeout)
def All(request, model):
    tmp = [jsonify(o) for o in model.objects.all()]    
    return HttpResponse("[%s]" % ",".join(tmp))

@cache_page(_timeout)
def Get(request, model, id):
    m = model.objects.get(pk=id)
    return HttpResponse(jsonify(m))

@cache_page(_timeout)
def Find(request, model, options):
    #we need to do this b/c request.GET is an invalid dict to pass in
    opts = dict([(str(x),request.GET[x]) for x in request.GET.keys()])
    tmp = [jsonify(o) for o in model.objects.filter(**opts)]
    #print tmp
    return HttpResponse("[%s]" % ",".join(tmp))
    
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

#NOTE: after testing--caching seems to just be slower!!!
#@cache_page(_timeout)
def loader(request, model):
    """Given a django model as a url param, this returns the meta information
    so that an equivalent javascript class can be constructed"""
    _model = getattr(MODELS, model)
    fields = [field.name for field in _model._meta.fields]
    #add virtualfields
    if '_virtualfields' in dir(_model._meta):
        fields.extend(_model._meta._virtualfields)
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
                if '_donotSerialize' in dir(modelObj._meta) and \
                       f.name in modelObj._meta._donotSerialize:
                    #check the _donotSerialize list --- they aren't enumerated
                    #we just return their pk
                    val = val.id
                else:
                    val = ModelEncoder._modelAsDict(val)
            elif isinstance(val, FieldFile) or isinstance(val, date) or \
                     isinstance(val, datetime):
                val = str(val)
            tmp[f.name] = val
        #enumerate virtual fields --e.g. paper.lab or paper.factors
        #NOTE: djanto has a _meta.virtual_fields; we are using
        #_meta._virtualfield; i hope that isn't confusing
        if '_virtualfields' in dir(modelObj._meta):
            for f in modelObj._meta._virtualfields:
                if f and getattr(modelObj, f):
                    #check to see if it's a ManyToMany Field:
                    val = getattr(modelObj, f)
                    if val.__class__.__name__ == "ManyRelatedManager":
                        #THIS seems to be too much!--but it is also right
                        #val = [ModelEncoder._modelAsDict(s) for s in val.all()]
                        #just return the obj.ids
                        val = [s.id for s in val.all()]
                    tmp[f] = val

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
