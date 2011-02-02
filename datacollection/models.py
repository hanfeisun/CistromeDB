from django.db import models
from django.contrib.auth.models import User
import os

try:
    import json
except ImportError:
    import simplejson as json
    
#drop?
SPECIES_CHOICES = (
    (u'hg', u'homo sapien'),
    (u'mm', u'mus musculus'),
    )
#drop?
EXPERIMENT_TYPE_CHOICES = (
    (u'chip', u'ChIP-Chip'),
    (u'seq', u'ChIP-Seq'),
    )

SUBMISSION_STATUS = (
    (u'pending', u'Pending'),
    (u'closed', u'Imported/Closed'),
    (u'n/a', u'Not Appropriate'),
    )

PAPER_STATUS = (
    (u'imported', u'imported awaiting download'),
    (u'downloaded', u'datasets downloaded awaiting analysis'),
    (u'complete', u'analysis complete/complete'),
    (u'error', u'error/hold- see comments'),
    )

DATASET_STATUS = (
    (u'imported', u'imported awaiting file download'),
    (u'downloaded', u'downloaded/closed'),
    (u'error', u'error/hold- see comments'),
    )

#pending is the default submission status
DEFAULT_SUBMISSION_STATUS = SUBMISSION_STATUS[0][0]

class DCModel(models.Model):
    """Implements common fns that will be inherited by all of the models
    NOTE: this is an ABSTRACT class, otherwise django will try to make a db
    for it.
    """
    class Meta:
        abstract = True
        
    def to_json(self):
        """Returns the model as a json strong"""
        tmp = {}
        for k in self.__dict__.keys():
            tmp[k] = "%s" % self.__dict__[k]
        return json.dumps(tmp)


class Papers(DCModel):
    """Papers are publications that are publicly available on Pubmed and Geo.
    The fields are:
    pmid - the pubmed id of the publication
    gseid - the GEO series id associated with the publication
    user - the user who currated the dataset
    title - the title of the publication
    abstract - the abstract of the publication
    pub_date - the publication date
    authors - list of the paper's authors
    corresponding_email - the email address of the last/corresponding author
    --Should we have this?

    diseas_state - the disease state of the samples used in the paper
    platform - the platform, e.g. Affymetrix Human Genome Version 2.0
    species - the species
    factor - the factor used in the paper, e.g. PolII
    cell_type - the cell type used in the paper, e.g. embryonic stem cell
    cell_line, cell_pop, strain - the cell line used in the paper
    condition - the condition used in the paper, e.g. PTIP-knockout
    """
    pmid = models.IntegerField(unique=True)
    gseid = models.CharField(max_length=8,unique=True)
    user = models.ForeignKey(User)
    title = models.CharField(max_length=255)
    abstract = models.TextField()
    pub_date = models.DateField()
    date_collected = models.DateTimeField()
    authors = models.CharField(max_length=255)
    #last_auth_email = models.EmailField()
    
    #MAY DROP the fields below!
#     disease_state = models.CharField(max_length=255, blank=True)
#     #platform_id = models.IntegerField(default=0) #change this to ForeignKey
#     platform = models.ForeignKey('Platforms', default=0)
#     species = models.CharField(max_length=2, choices=SPECIES_CHOICES,
#                                blank=True)
#     cell_type = models.ForeignKey('CellTypes', default=0)
#     cell_line = models.ForeignKey('CellLines', default=0)
#     cell_pop = models.ForeignKey('CellPops', default=0)
#     strain = models.ForeignKey('Strains', default=0)
#     condition = models.ForeignKey('Conditions', default=0)
    
    journal = models.ForeignKey('Journals', default=0)
    status = models.CharField(max_length=255, choices=PAPER_STATUS,
                              default="imported")
    #a place for curators to add comments
    comments = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Datasets(DCModel):
    """Datasets are the data associated with the papers.  They are usually
    available for download from Geo.
    The fields are:
    gsmid - GEO sample identifier
    chip_page - (not sure) the url of the platform? (optional)
    control_gsmid - GEO sample identifier for control (optional)
    control_page - (not sure) the url of the platform? (optional)
    date_collected - the date we collected the sample from GEO
    file - file path ref
    user_id - the user who currated the dataset
    paper_id - the paper that the dataset is associated with
    factor_id - the factor associated with the sample

    NOTE: from here on out, they are all optional, and they override the
    paper field. e.g. if platform is defined for a dataset, then it takes
    precedence over the dataset's paper's platform.  IF it is not defined,
    then it inherits the paper's info.
    
    platform - the platform, e.g. Affymetrix Human Genome Version 2.0
    species - the sample's species
    factor - the sample's factor, e.g. PolII
    cell_type - the sample's cell type, e.g. embryonic stem cell
    cell_line, cell_pop, strain - the sample's cell line
    condition - the sample's condition, e.g. PTIP-knockout
    """
    def upload_to_path(self, filename):
        """Returns the upload_to path for this dataset.
        NOTE: we are going to store the files by gsmid, e.g. GSM566957
        is going to be stored in: datasets/gsm566/957.
        I'm not sure if this is the place to validate gsmids, but it may be"""
        return os.path.join('datasets','gsm%s' % self.gsmid[3:6],
                            self.gsmid[6:], filename)

    gsmid = models.CharField(max_length=9)
    #Name comes from "title" in the geo sample information
    name = models.CharField(max_length=255, blank=True)
    chip_page = models.URLField(blank=True)
    control_gsmid = models.CharField(max_length=9, blank=True)
    control_page = models.URLField(blank=True)
    date_collected = models.DateTimeField()
    file = models.FileField(upload_to=upload_to_path, null=True)
    file_url = models.URLField(max_length=255, blank=True)
    file_type = models.ForeignKey('FileTypes')
    user = models.ForeignKey(User)
    paper = models.ForeignKey('Papers')
    factor = models.ForeignKey('Factors', default=0)

    platform = models.ForeignKey('Platforms', default=0)
    species = models.ForeignKey('Species')
    assembly = models.ForeignKey('Assembly', default=0)
    #in description, we can add additional info e.g. protocols etc
    description = models.TextField(blank=True)
    cell_type = models.ForeignKey('CellTypes', default=0)
    cell_line = models.ForeignKey('CellLines', default=0)
    cell_pop = models.ForeignKey('CellPops', default=0)
    strain = models.ForeignKey('Strains', default=0)
    condition = models.ForeignKey('Conditions', default=0)
    
    status = models.CharField(max_length=255, choices=PAPER_STATUS,
                              default="imported")
    comments = models.TextField(blank=True)

class Platforms(DCModel):
    """Platforms are the chips/assemblies used to generate the dataset.
    For example, it can be an Affymetrix Human Genome U133 Plus 2.0 Array,
    i.e. GPLID = GPL570
    The fields are:
    name- name of the platform
    gplid - GEO Platform ID
    experiment type- Choice: ChIP-Chip/ChIP-Seq
    """
    gplid = models.CharField(max_length=7)
    name = models.CharField(max_length=255, blank=True)
    technology = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    #experiment_type = models.CharField(max_length=10,
    #choices=EXPERIMENT_TYPE_CHOICES)
    def __str__(self):
        return self.name


class Factors(DCModel):
    """The factors applied to the sample, e.g. PolII, H3K36me3, etc."""
    name = models.CharField(max_length=255)
    antibody = models.CharField(max_length=255, blank=True)
    def __str__(self):
        return self.name

class CellTypes(DCModel):
    """Sample's tissue/cell type, e.g. embryonic stem cell, b lymphocytes, etc.
    """
    name = models.CharField(max_length=255)
    tissue_type = models.CharField(max_length=255, blank=True)
    def __str__(self):
        return self.name

class CellLines(DCModel):
    """Sample's cell lines.  I really don't know what distinguishes
    cell lines from cell populations or strains and mutations, but i'm going
    to create the tables just to be inclusive
    """
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class CellPops(DCModel):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Strains(DCModel):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name
    
class Conditions(DCModel):
    """Experiment/sample conditions, e.g. PTIP-knockout, wild-type"""
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Journals(DCModel):
    """Journals that the papers are published in"""
    name = models.CharField(max_length=255)
    issn = models.CharField(max_length=9)
    impact_factor = models.FloatField(default=0.0)
    def __str__(self):
        return self.name

class PaperSubmissions(DCModel):
    """Public paper submission page
    we collect the ip address of the submitter just in case of malicious usr
    pmid - pubmed id,
    gseid - GEO series id,
    NOTE: either pmid or gseid must be submitted
    status- see submission status,
    user- curator who last handled this submission
    ip_addr - the ip address of the submitter
    submitter_name - optional name of the submitter
    comments - any comments a currator might attach to the submission
    """
    pmid = models.IntegerField(default=0)
    gseid = models.CharField(max_length=8, blank=True)
    status = models.CharField(max_length=255, choices=SUBMISSION_STATUS)
    user = models.ForeignKey(User, default=1) #default to a valid user:lentaing
    ip_addr = models.CharField(max_length=15)
    submitter_name = models.CharField(max_length=255, blank=True)
    comments = models.TextField(blank=True)

class FileTypes(DCModel):
    """File types for our geo datasets"""
    name = models.CharField(max_length=20)

class Species(DCModel):
    name = models.CharField(max_length=255)
    
class Assembly(DCModel):
    name = models.CharField(max_length=255)
    pub_date = models.DateField(blank=True)
    
