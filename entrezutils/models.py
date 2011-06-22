import urllib
from xml.dom.minidom import parseString
from xml.dom.minidom import Node

from django.db import models

try:
    import json
except:
    import simplejson as json
    

class XMLWrapper:
    """parses and stores an XML tree as follows:
    <elm0>
       <elm1 x=1 y=2>
          <elm2><elm3>foo</elm3></elm2>
       </elm1>
    <elm4>
       <elm5>bar</elm5>
    </elm4>
    <elm6/>
    </elm0>
    RETURNS: the following dictionary
    {_tagName="elm0", _attribs={},
    _children:[{_tagName="elm1", _attribs= {x:1, y:2},
                _children:[{_tagName="elm2", _attribs={},
                            _children:[{_tagName="elm3", _attribs={},
                                        _children:["foo"]}]
                            }]
                },
                {_tagName="elm4", _attribs={},
                 _children=[{_tagName="elm5", _attribs={},
                             _children:["bar"]}]
                },
                {_tagName="elm6", _attribs={}, _children:[]}
                ]}
    """
    def __init__(self, root_node):
        """given an XML DOM Tree, constructs the dictionary as described
        above"""
        self.root = self._parseDOM(root_node)

    def _parseDOM(self, node):
        """Constructs a dictionary that represents the XML node"""
        if node.nodeType == Node.TEXT_NODE:
            return node.nodeValue.strip()
        
        tmp = {'_tagName':node.tagName}
        if node.hasAttributes():
            attribs = {}
            for i in range(node.attributes.length):
                attribs[node.attributes.item(i).name] = \
                                                 node.attributes.item(i).value
            #print attribs
            tmp['_attribs'] = attribs
        if node.hasChildNodes():
            if len(node.childNodes) == 1 and \
               node.childNodes[0].nodeType == Node.TEXT_NODE and \
               node.childNodes[0].nodeValue.strip() != '':
                tmp['_value'] = node.childNodes[0].nodeValue.strip()
                tmp['_children'] = None
            else:
                children = filter(lambda x: x != '',
                                  [self._parseDOM(c) for c in node.childNodes])
                if len(children):
                    tmp['_children'] = children
                else:
                    tmp['_children'] = None
        else:
            tmp['_children'] = None

        return tmp
        
    def getElementsByTagName(self, tagName):
        """Returns an array of elements that match the tagName"""
        tmp = []
        def fn(node):
            if node['_tagName'] == tagName:
                tmp.append(node)
        treeWalker(self.root, fn)
        return tmp

def treeWalker(XMLWrapperNode, fn):
    """Walks XMLWrapper tree in BFS order, and applies the fn"""
    fn(XMLWrapperNode)
    if XMLWrapperNode['_children']:
        for x in XMLWrapperNode['_children']:
            treeWalker(x, fn)

def GeoQuery(accession):
    """We can access geo data over HTTP using the following url:
    http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=XXX&view=quick&form=xml&targ=self
    where XXX is the GEO accession string, e.g. GSE20852, GSM1137

    This call will return an xml file, which we will have to parse and store
    in the instance.

    So this is a data-holder class for the GEO xml files that are being made.
    OF course, all of this is hidden from the user, so all he does is:
    tmp = GEO('GSE20852')

    NOTE: this technically isn't a DJANGO model, but i've put it in this module
    b/c it's the best place for now
    """
    URL = "http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=%s&view=quick&form=xml&targ=self" % accession

    f = urllib.urlopen(URL)
    #print f.read()
    dom = parseString(f.read())
    f.close()
    tmp = XMLWrapper(dom.documentElement)
    #print tmp
    return tmp

def EntrezQuery(tool, params):
    """We can programmatically access any Entrez db using eutils.
    For example, we can look up pubmed records using the following url:
    http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=20671152
    
    The HTTP call returns an XML file which we can parse.  This fn returns
    a dictionary representation of that XML file.

    Inputs:
    tool - string of the tool name (see below)
    params - dictionary of parameters to pass

    NOTE: there are 8 eutil tools- esearch, epost, esummary, efetch, elink,
    einfo, egquery, espell.

    OF these, the most commonly used (for our purposes) are: esummary, elink,
    and occasionally efetch, esearch.

    NOTE: if Entrez becomes a robust app, then maybe I'll support the other
    tools, but for now, I'm just going to support the two main tools-- esummary
    and elink; and secondarily efetch and esearch.
    """
    
    URLparams = "&".join(["%s=%s" % (k, params[k]) for k in params])
    
    URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/%s.fcgi?%s" % \
          (tool, URLparams)
    #print URL
    f = urllib.urlopen(URL)
    dom = parseString(f.read())
    f.close()
    
    tmp = XMLWrapper(dom.documentElement)
    return tmp
    #print tmp.root

#------------------------------------------------------------------------------

class PubmedSummary:
    """stores the information from a pubmed summary:--usually the stuff from
    an esummary call on a pubmed id:
    pmid - pubmed id
    gseid - geo series id
    title - paper title
    authors - list of authors
    abstract - paper abstract
    published - e.g. Science, Aug. 2010

    --SUPPORTS auto_import_paper page
    """
    
    def __init__(self, pmid):
        self._attrs = ['pmid', 'gseid', 'title', 'authors', 'abstract',
                       'pub_date', 'journal', 'issn', 'published']
        self.pmid = pmid

        params0 = {'db':'pubmed', 'id': pmid}
        pubmed = EntrezQuery('esummary', params0)
        pubmedItems = pubmed.getElementsByTagName("Item")
        if len(pubmedItems):
            #NOTE: almost all of the fields should come from pubmed!!!
            #gseid - below in geo
            self.title = filter(lambda node:node['_attribs']['Name']=='Title',
                                pubmedItems)[0]['_value']
            auths = filter(lambda node: node['_attribs']['Name'] == 'Author',
                         pubmedItems)
            self.authors = [n['_value'] for n in auths]
            #abstrac - below in geo

            #search for the item where attribute Name='PubDate' and 'Source'
            self.pub_date=filter(lambda nd:nd['_attribs']['Name']=='PubDate',
                                 pubmedItems)[0]['_value']
            self.journal=filter(lambda node:node['_attribs']['Name']=='Source',
                                pubmedItems)[0]['_value']
            self.issn = filter(lambda node: node['_attribs']['Name'] == 'ISSN',
                               pubmedItems)[0]['_value']
            self.published = "%s, %s" % (self.journal, self.pub_date)

        #print pubmed.root
        
        params1 = {'dbfrom':'pubmed', 'db':'gds', 'id':pmid}
        ent = EntrezQuery("elink", params1)
        
        lsd = ent.getElementsByTagName('LinkSetDb')
        if len(lsd):
            gdsid = lsd[0]['_children'][2]['_children'][0]['_value']
            params2 = {'db':'gds', 'id':gdsid}
            gds = EntrezQuery('esummary', params2)

            items = gds.getElementsByTagName('Item')
            
            #search for the item where attribute Name='GSE'
            tmp = filter(lambda node: node['_attribs']['Name'] == 'GSE',
                         items)
            self.gseid = "GSE"+tmp[0]['_value']

            self.abstract=filter(lambda nd:nd['_attribs']['Name']=='summary',
                                 items)[0]['_value']

    def __str__(self):
        """returns the string repr of the PubmedSummary"""
        #attr = ['pmid', 'gseid', 'title', 'authors', 'abstract', 'published']
        return "\n".join(["%s:%s" % (a, getattr(self, a)) \
                          for a in self._attrs])

    def to_json(self):
        """returns the json repr of the PubmedSummary"""
        tmp = ",".join(["'%s':%s" % (a, json.dumps(getattr(self, a))) \
                        for a in self._attrs])
        return "{%s}" % tmp
#------------------------------------------------------------------------------
# Adapter classes have moved to datacollection/entrez.py
