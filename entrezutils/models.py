import urllib
from django.db import models
from pyquery import PyQuery

pq = lambda p: PyQuery(p, parser="xml")

try:
    import json
except:
    import simplejson as json

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
    #ENSURE mode=xml is a param
    if 'mode' not in params:
        params['mode'] = 'xml'

    URLparams = "&".join(["%s=%s" % (k, params[k]) for k in params])

    URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/%s.fcgi?%s" %\
          (tool, URLparams)
    return pq(URL)
    #print tmp.root


class PubmedArticle:
    """like pubmed summary, BUT instead of going to geo for the abstract,
    we actually get the full pubmed record.
    NOTE: the key is to use efetch instead of esummary!

    --Supports the auto_import_paper page, and will replace PubmedSummary
    for pubmed retrievals
    """

    @staticmethod
    def _getValue(nodeList, field, val):
        """within the nodelist, tries to field the field that matches the
        val, and return the _value
        """
        tmp = filter(lambda x: x[field] == val, nodeList)
        if len(tmp) > 0:
            return tmp[0]['_value']
        return None

    def __init__(self, pmid):
        self._attrs = ['pmid', 'geo', 'title', 'authors', 'abstract',
                       'pub_date', 'journal', 'issn', 'published']
        self.pmid = pmid
        self.geo = []

        efetch_param = {'db': 'pubmed', 'id': pmid, 'mode': 'xml'}
        pubmed_d = EntrezQuery('efetch', efetch_param)
        pub_date = pubmed_d("DateCreated").children("Year, Month, Day").text()



        #NOTE: in journal, there's the official title, and the common name
        #<Title>Science (New York, N.Y.)</Title>
        #<ISOAbbreviation>Science</ISOAbbreviation>
        #self.journal = helper(journal['_children'], "Title")
        self.pub_date = pub_date.replace(" ", "-")
        self.title = pubmed_d("ArticleTitle").text()
        self.journal = pubmed_d("Journal ISOAbbreviation").text()
        self.issn = pubmed_d("Journal ISSN").text()
        self.published = "%s, %s" % (self.journal, self.pub_date)

        auths = pubmed_d("Author")
        lst = []
        for i in range(len(auths)):
            author = auths.eq(i)
            lastn = author.find("LastName").text()
            inits = author.find("Initials").text()
            lst.append("%s %s" % (lastn, inits))
        self.authors = lst
        self.abstract = pubmed_d("AbstractText").text()


        #NOTE: geo is a list of geos
        gseid = pubmed_d("AccessionNumber")
        if gseid:
            self.geo = gseid.map(lambda i, el: {"gseid": el.text})

        else:

            #try to get the geo from geo
            elink_param = {'dbfrom': 'pubmed', 'db': 'gds', 'id': pmid}
            elink_d = EntrezQuery("elink", elink_param)

            gdsid = elink_d("LinkSetDb DbTo:contains('gds') ~ Link Id")

            if gdsid:
                for a_gdsid in gdsid:
                    # TODO: extend for all gdsid
                    esum_param = {'db': 'gds', 'id': a_gdsid.text}
                    gds_d = EntrezQuery('esummary', esum_param)
                    gseid = gds_d("Item[Name=GSE]")
                    if gseid:
                        new_gse = {"gseid": "GSE" + gseid.text(),
                                   "gsetitle":gds_d("DocSum Item[Name=title]").text(),
                                   "gsm": [],
                                   "species": gds_d("Item[Name=taxon]").text(),
                                   "type":gds_d("Item[Name=gdsType]").text()}
                        self.geo.append(new_gse)

                        samples =  gds_d("Item[Type='Structure'][Name='Sample']")
                        samples = sorted(list(samples),key=lambda s:pq(s)("[Name='Accession']").text())
                        for g in samples:
                            new_gse['gsm'].append({'gsmid': pq(g)("[Name='Accession']").text(),
                                                   'gsmtitle': pq(g)("[Name='Title']").text()})



    def to_json(self):
        """returns the json repr of the PubmedArticle"""
        tmp = ",".join(['"%s":%s' % (a, json.dumps(getattr(self, a)))\
                        for a in self._attrs])
        return "{%s}" % tmp

#------------------------------------------------------------------------------
# Adapter classes have moved to datacollection/entrez.py
