from entrezutils import models as entrez

class PaperAdapter:
    """Given a GSEID (given from a PaperSummary), this class adapter holds
    all of the information necessary to create a Paper object"""
    
    def __init__(self, pmid):
        pubmed = entrez.PubmedSummary(pmid)

        #self.pmid = geo.getElementsByTagName("Pubmed-ID")[0]['_value']
        self.pmid = pmid
        self.gseid = pubmed.gseid
        self.title = pubmed.title
        self.abstract = pubmed.abstract
        #self.pub_date = pubmed.pub_date #Can't take this b/c not in YYYY-MM-DD
        self.authors = pubmed.authors
        self.journal = pubmed.journal
        self.issn = pubmed.issn
        
        geo = entrez.GeoQuery(self.gseid)
        self.pub_date = geo.getElementsByTagName("Release-Date")[0]['_value']
        contributors = geo.getElementsByTagName("Contributor")

        self.design = geo.getElementsByTagName("Overall-Design")[0]['_value']
        self.type = geo.getElementsByTagName("Type")[0]['_value']

        #store the sample accession numbers
        samples = geo.getElementsByTagName('Sample')
        self.datasets = ["%s" % s['_children'][0]['_value'] for s in samples]

        #get the journal -- TAKEN from PaperSummary
        #NOTE: this is all in PaperSummary
        # params0 = {'db':'pubmed', 'id': self.pmid}
        # pubmed = entrez.EntrezQuery('esummary', params0)
        # pubmedItems = pubmed.getElementsByTagName("Item")
        # self.journal= filter(lambda node: node['_attribs']['Name']=='Source',
        #                      pubmedItems)[0]['_value']
        # self.issn = filter(lambda node: node['_attribs']['Name'] == 'ISSN',
        #                    pubmedItems)[0]['_value']
        
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
        self.raw_file_url = supplementary_data['_value']
        self.raw_file_type = supplementary_data['_attribs']['type']
        
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
