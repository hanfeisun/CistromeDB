"""
Given a set of simple classifiers, confederates them into a single classifier
"""
import os
import sys
import re
import random
import pickle

import nltk

#import factorsGenerator
def document_features(document, word_features): 
    """a document feature extractor taken from:
    Natural Language Processing with Python - Bird, Klein, and Loper 
    O'Reilly 2009
    Chapter 6
    
    NOTE: for some reason when i use the set document it returns this:
    set(['\n', ' ', ')', '(', '-', '/', '.', '1', '0', '3', '2', '5', '4', '7', '6', '9', ':', 'A', 'C', 'B', 'E', 'D', 'G', 'F', 'I', 'H', 'M', 'L', 'O', 'N', 'Q', 'P', 'S', 'R', 'U', 'T', 'V', 'Y', 'X', 'Z', '_'])
    """
    document_words = document.split("\n") #THIS IS BUGGY! -set(document) 
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words) 
    return features

def loadClassifiers(classifier_dir = "classifiers"):
    """returns a list of (classifier, wordFeatures, label) -- 
    the label is just the filename
    """
    ret = []
    for c in os.listdir(classifier_dir):
        if c.endswith(".dat"):
            wd = classifier_dir
            name = ".".join(c.split(".")[:-1])

            #check the optional override directory classifers/override/
            #***NOTE: A .dat file must be in the top-level dir--otherwise
            #         we won't satify the if-condition above
            if os.path.exists(os.path.join(wd, 'override', c)):
                #SILENCED for now
                #print "Manual: %s" % name
                wd = os.path.join(wd, 'override')

            #load classifier
            f = open(os.path.join(wd, c))
            classifier = pickle.load(f)
            f.close()

            #load wordFeatures
            f = open(os.path.join(wd, "%s.txt" % name))
            #NOTE: NO need to fear about '' in wordFeatures--even when 
            #there is a lagging EOLN at the EOF
            #NOTE: THIS IS DIFFERENT FROM factorsClassifier--
            #we are using concepts here, so split by NEW LINE
            wordFeatures = f.read().split("\n")
            f.close()

            ret.append((classifier, wordFeatures, name))
    return ret

def _classifyOne(classifier, featureset):
    """Given a SIMPLE classifier and a document, return the classification
    i.e. the probability that it is True
    """
    c = classifier.prob_classify(featureset)
    #NOTE: c is a prob dist who has two "samples"/labels, True/False
    #return the probability of True
    return c.prob(True)

def classify(simpleClassifiers, document):
    """Given a set of simpleClassifiers - list of tuples from classifiers above
    (classifier, wordFeatures, name)
    and a document
    return it's classification
    """
    ls = []
    for (c, wf, name) in simpleClassifiers:
        fs = document_features(document, wf)
        ls.append((_classifyOne(c, fs), name))
    return sorted(ls, key=lambda x: x[0], reverse=True)

#AUTO-load classifiers
#a trick to get the current module 
_modname = globals()['__name__']
_this_mod = sys.modules[_modname]
for d in  os.listdir(_this_mod.__path__[0]):
    #HACK: module names don't have a .
    if d.find(".") == -1:
        path = os.path.join(_this_mod.__path__[0], d)
        tmp = loadClassifiers(path)
        setattr(_this_mod, d, tmp)

