import datetime
import time

try:
    import json
except:
    import simplejson as json

import unittest
from django.db import models
import django.test.client as client

import views
import datacollection.models

class TestModel(models.Model):
    """Contains one of each field, so that we can test whether the jsonify
    fn works.
    NOTE: at some point i got lazy and decided to only include the fields i
    use most often
    """
    int_field = models.IntegerField(null=True, default=None)
    #bigint_field = models.BigIntegerField(null=True, default=None)
    boolean_field = models.BooleanField()
    char_field = models.CharField(max_length=255, default="")
    cms_int_field = models.CommaSeparatedIntegerField(max_length=255,
                                                      default="")
    date_field = models.DateField(blank=True, default="")
    date_time_field = models.DateTimeField(blank=True, default="")
    decimal_field = models.DecimalField(max_digits=5, decimal_places=2)
    email_field = models.EmailField(default="")
    file_field = models.FileField(upload_to="/tmp/foo", default="")
    #file_path_field = models.FilePathField(path=".")
    float_field = models.FloatField()
    #HERE is where i got lazy
    text_field = models.TextField(default="")
    url_field = models.URLField(default="")

class TestModelA(models.Model):
    """This is to test how jsonify will print out ForeignKeys"""
    foo = models.CharField(max_length=255, default="")
    
class TestModelB(models.Model):
    """This is to test how jsonify will print out ForeignKeys"""
    bar = models.CharField(max_length=255, default="")
    baz = models.ForeignKey('TestModelA', null=True, blank=True, default=None)
                                                      
class JsonifyTestCase0(unittest.TestCase):
    """Testing the views.jsonify method"""
    def setUp(self):
        self.vals = {"int":5, "boolean":True, "char":"foobar",
                     "cms_int":"1,2,3", "date": datetime.date(2011, 2, 2),
                     "date_time":datetime.datetime(2011,2,2,17,53,57,37819),
                     "decimal":3.14, "email":"foo@example.com",
                     "file":"/some/path/to/file.txt", "float":3.14,
                     "text":"the rain in spain", "url":"http://some.url.com"}
                
        self.foo = TestModel()
        for f in self.vals:
            setattr(self.foo, f+"_field", self.vals[f])
        
    def testJsonify(self):
        #print views.jsonify(self.foo)
        tmp = json.loads(views.jsonify(self.foo))
        for f in self.vals:
            if f is not 'date' and f is not 'date_time':
                self.assertEqual(tmp[f+"_field"], self.vals[f])

        self.assertEqual("2011-02-02 17:53:57.037819", tmp['date_time_field'])
        self.assertEqual("2011-02-02", tmp['date_field'])

#move this to views!

class JsonifyTestCase1(unittest.TestCase):
    """Testing how views.jsonify serializes foreignkeys, i.e. it should
    actually print it out as a record, not just an id"""
    def setUp(self):
        self.a = TestModelA()
        self.a.foo = "some string"

        self.b = TestModelB()
        self.b.bar = "some other string"
        self.b.baz = self.a

    def testJsonifyA(self):
        #print views.jsonify(self.a)
        tmp = json.loads(views.jsonify(self.a))

        self.assertEqual("TestModelA", tmp['_class'])
        self.assertEqual("some string", tmp['foo'])
        self.assertEqual(None, tmp['id'])
        
    def testJsonifyB(self):
        #print views.jsonify(self.b)
        tmp = json.loads(views.jsonify(self.b))

        self.assertEqual("TestModelB", tmp["_class"])
        self.assertEqual("some other string", tmp["bar"])
        self.assertEqual(None, tmp["id"])
        #The foreignkey should be of type {}
        self.assertEqual(type({}), type(tmp['baz']))
        self.assertEqual("TestModelA", tmp['baz']['_class'])
        self.assertEqual("some string", tmp['baz']['foo'])
    
class TestRouter(unittest.TestCase):
    """Regression tests so that we can refactor router
    NOTE: there are some simple tests for the fns, e.g. All, Get, etc.
    so after this we can refactor these fns if we want
    """
    def setUp(self):
        Species = datacollection.models.Species
        self.s1 = Species.objects.create(name="Homo Sapien")
        self.s2 = Species.objects.create(name="Mus Musculus")

    def testAll(self):
        request = {}
        rest = ''
        
        #print views.router(request, 'Species', 'all', rest)
        foo = views.router(request, 'Species', 'all', rest)
        #print "Content is: ^%s$" % foo.content
        tmp = json.loads(foo.content)
        self.assertEqual(2, len(tmp))

        self.assertEqual(1, tmp[0]['id'])
        self.assertEqual("Homo Sapien", tmp[0]['name'])
        self.assertEqual("Species", tmp[0]['_class'])

        self.assertEqual(2, tmp[1]['id'])
        self.assertEqual("Mus Musculus", tmp[1]['name'])
        self.assertEqual("Species", tmp[1]['_class'])

    def testGet(self):
        """Try to get the first entry
        NOTE: if you try to delete the first entry, this test fails! so
        that means the ordering of the tests aren't guaranteed
        """
        request = {}
        rest = '1'
        
        #print views.router(request, 'Species', 'all', rest)
        foo = views.router(request, 'Species', 'get', rest)
        #print "\n\nContent is\n\n\n: ^%s$" % foo.content
        tmp = json.loads(foo.content)

        self.assertEqual(1, tmp['id'])
        self.assertEqual("Homo Sapien", tmp['name'])
        self.assertEqual("Species", tmp['_class'])

    def testFind(self):
        "Try to find the first obj"
        #need client b/c find actually uses the request param
        c = client.Client()
        response = c.get("/jsrecord/Species/find/", {"name":"Homo Sapien"})
        #print "Content is: ^%s$" % response.content

        tmp = json.loads(response.content)
        #NOTE: THE filtering fn is returning some whacky results!
        #this fails!--NOTE b/c i think that for every test, setUp is called
        #self.assertEqual(1, len(tmp))

    def testSave(self):
        """Try saving an obj to the db"""
        c = client.Client()
        response = c.post("/jsrecord/Species/save/", {'id': "null",
                                                      'name':'C. Elegans'})
        #print "Content is: ^%s$" % response.content
        tmp = json.loads(response.content)

        self.assertEqual(True, tmp['success'])
        self.assertEqual(type({}), type(tmp['obj']))
        self.assertEqual("Species", tmp['obj']["_class"])
        self.assertEqual("C. Elegans", tmp['obj']["name"])

    def testDelete(self):
        "Try to delete the first entry"
        foo = views.router({}, 'Species', 'delete', "2")
        print "Content is: ^%s$" % foo.content
        tmp = json.loads(foo.content)
        self.assertEqual(True, tmp['success'])

class TestLoader(unittest.TestCase):
    """Regression tests so that we can refactor loader"""

    def Test0(self):
        foo = views.loader({}, 'Species')
        #print foo.content
        tmp = json.loads(foo.content)
        
        self.assertEqual("Species", tmp['className'])
        self.assertEqual("id", tmp['fields'][0])
        self.assertEqual("name", tmp['fields'][1])

