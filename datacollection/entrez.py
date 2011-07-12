from entrezutils import models as entrez

class PaperAdapter:
    """Given a GSEID (given from a PaperSummary), this class adapter holds
    all of the information necessary to create a Paper object"""
    
    def __init__(self, pmid):
        pubmed = entrez.PubmedArticle(pmid)

        self.pmid = pmid
        #NOTE: pubmed article returns a list of gseids!
        self.gseid = pubmed.gseid[0]
        self.title = pubmed.title
        self.abstract = pubmed.abstract
        self.pub_date = pubmed.pub_date 
        self.authors = pubmed.authors
        self.journal = pubmed.journal
        self.issn = pubmed.issn
        
        geo = entrez.GeoQuery(self.gseid)
        #self.pub_date = geo._getValue("Release-Date")
        #contributors = geo.getElementsByTagName("Contributor")

        self.design = geo._getValue("Overall-Design")
        self.type = geo._getValue("Type")

        #store the sample accession numbers
        samples = geo.getElementsByTagName('Sample')
        self.datasets = ["%s" % s['_children'][0]['_value'] for s in samples]
        
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
