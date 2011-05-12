from entrezutils import models as entrez

class PaperAdapter:
    """Given a GSEID (given from a PaperSummary), this class adapter holds
    all of the information necessary to create a Paper object"""
    
    def __init__(self, gseid):
        geo = entrez.GeoQuery(gseid)
        
        self.pmid = geo.getElementsByTagName("Pubmed-ID")[0]['_value']
        self.gseid = gseid
        self.title = geo.getElementsByTagName("Title")[0]['_value']
        self.abstract = geo.getElementsByTagName("Summary")[0]['_value']
        self.pub_date = geo.getElementsByTagName("Release-Date")[0]['_value']

        contributors = geo.getElementsByTagName("Contributor")
        #ERROR: authors list should come from pubmed
        pubmed = entrez.PubmedSummary(self.pmid)
        self.authors = pubmed.authors
#         self.authors = []
#         for a in contributors:
#             person = a['_children'][0]['_children']
#             #NOTE: form is LASTNAME FM - where F is first initial, and M is mid
#             if len(person) < 3: 
#                 first = person[0]['_value']
#                 last = person[1]['_value']
#                 self.authors.append("%s %s" % (last, first[0]))
#             else: 
#                 first = person[0]['_value']
#                 middle = person[1]['_value']
#                 last = person[2]['_value']
#                 self.authors.append("%s %s%s" % (last, first[0], middle[0]))

        self.design = geo.getElementsByTagName("Overall-Design")[0]['_value']
        self.type = geo.getElementsByTagName("Type")[0]['_value']

        #store the sample accession numbers
        samples = geo.getElementsByTagName('Sample')
        self.datasets = ["%s" % s['_children'][0]['_value'] for s in samples]

        #get the journal -- TAKEN from PaperSummary
        params0 = {'db':'pubmed', 'id': self.pmid}
        pubmed = entrez.EntrezQuery('esummary', params0)
        pubmedItems = pubmed.getElementsByTagName("Item")
        self.journal= filter(lambda node: node['_attribs']['Name'] == 'Source',
                             pubmedItems)[0]['_value']
        self.issn = filter(lambda node: node['_attribs']['Name'] == 'ISSN',
                           pubmedItems)[0]['_value']
        
    def __str__(self):
        attrs = ["pmid", "gseid", "title", "abstract", "pub_date", "authors",
                 "design", "type", "datasets", "journal"]
        return "\n".join(["%s:%s" % (a, getattr(self, a)) for a in attrs])

class DatasetAdapter:
    """Given a GSMID, this class adapter holds all of the information
    needed to create a Dataset instance.
    NOTE: things like factor, cell line, cell pop, strain, etc. must be
    currated b/c the geo info for each GSM isn't standardized
    """
    def __init__(self, gsmid):
        geo = entrez.GeoQuery(gsmid)

        self._attrs = ["gsmid", "name", "platform", "species", "file_url",
                       "file_type"]

        self.gsmid = gsmid
        self.name = geo.getElementsByTagName("Title")[0]['_value']
        self.platform = geo.getElementsByTagName("Platform")[0]['_children'][0]['_value']
        self.species = geo.getElementsByTagName("Organism")[0]['_value']
        supplementary_data = geo.getElementsByTagName("Supplementary-Data")[0]
        self.file_url = supplementary_data['_value']
        self.file_type = supplementary_data['_attribs']['type']
        
    def __str__(self):
        return "\n".join(["%s:%s" % (a, getattr(self, a)) \
                          for a in self._attrs])

class PlatformAdapter:
    """Given a GPLID, this class adapter holds all of the information about
    a platform"""
    def __init__(self, gplid):
        geo = entrez.GeoQuery(gplid)
        
        self.gplid = gplid
        self.name = geo.getElementsByTagName("Title")[0]['_value']
        self.technology = geo.getElementsByTagName("Technology")[0]['_value']
        self.species = geo.getElementsByTagName("Organism")[0]['_value']
        
        #YUCK!
        if '_value' in geo.getElementsByTagName("Manufacturer")[0]:
            self.company = geo.getElementsByTagName("Manufacturer")[0]['_value']
        else:
            self.company = ""


    def __str__(self):
        attrs = ["gplid", "name", "technology", "species", "company"]
        return "\n".join(["%s:%s" % (a, getattr(self, a)) for a in attrs])
