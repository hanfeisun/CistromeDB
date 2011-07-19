from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import smart_str, smart_unicode
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
    (u'imported', u'paper entered awaiting datasets'),
    (u'datasets', u'datasets imported awaiting download'),
    (u'transfer', u'datasets download in progress'),
    (u'downloaded', u'datasets downloaded awaiting analysis'),
    (u'complete', u'analysis complete/complete'),
    (u'error', u'error/hold- see comments'),
    )

DATASET_STATUS = (
    (u'imported', u'imported awaiting meta-info'),
    (u'info', u'meta-info inputted awaiting validation'),
    (u'valid', u'meta-info validated awaiting file download'),
    (u'transfer', u'file is downloading'),
    (u'downloaded', u'downloaded/closed'),
    (u'error', u'error/hold- see comments'),
    )

SAMPLE_STATUS = (
    (u'new', u'sample created, awaiting check for raw files'),
    (u'checked', u'raw files checked, awaiting run'),
    (u'running', u'analysis is running, awaiting completion'),
    (u'complete', u'analysis complete'),
    (u'error', u'error/hold- see comments'),
    )

TEAMS = (
    (u'admin', u'Administrators'),
    (u'paper', u'paper collection team'),
    (u'data', u'data collection team'),
    )

FACTOR_TYPES = (
    (u'tf', u'transcription factor'),
    (u'hm', u'histone mark'),
    (u'other', u'other'),
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
    #def __init__(self, *args):
    #    super(Papers, self).__init__(*args)
    #    self._meta._donotSerialize = ['user']

    pmid = models.IntegerField(null=True, blank=True, default=None)
    gseid = models.CharField(max_length=255, null=True, blank=True, 
                             default="")
    user = models.ForeignKey(User, null=True, blank=True, default=None)
    title = models.CharField(max_length=255, null=True, blank=True, 
                             default="")
    abstract = models.TextField(null=True, blank=True, default="")
    pub_date = models.DateField(null=True, blank=True, default=None)
    date_collected = models.DateTimeField(null=True, blank=True, default=None)
    authors = models.CharField(max_length=255, null=True, blank=True, 
                               default="")
    last_auth_email = models.EmailField(null=True, blank=True, default=None)
        
    journal = models.ForeignKey('Journals',
                                null=True, blank=True, default=None)
    status = models.CharField(max_length=255, choices=PAPER_STATUS,
                              default="imported")
    #a place for curators to add comments
    comments = models.TextField(blank=True)

    def _get_species(self):
        """Returns a list of the species objs associated with the papers, i.e.
        the set of species that are found in the paper's datasets"""
        tmp = []
        samples = Samples.objects.filter(paper=self.id)
        for s in samples:
            if s.species and s.species.name not in tmp:
                tmp.append(smart_str(s.species.name))
        return tmp

    def _get_factors(self):
        """Returns a list of the factors associated w/ the paper, i.e.
        returns the set of factors that are found in the paper's datasets"""
        tmp = []
        samples = Samples.objects.filter(paper=self.id)
        for s in samples:
            if s.factor and s.factor.name not in tmp:
                tmp.append(smart_str(s.factor.name))
        return tmp

    def _get_lab(self):
        """Returns the last author in the authors list"""
        return smart_str(self.authors.split(",")[-1:][0])

    species = property(_get_species)
    factors = property(_get_factors)
    lab = property(_get_lab)
    
    def __str__(self):
        return smart_str(self.title)

#NOTE: _donotSerialize fields are not enumerated as records, just as keys
Papers._meta._donotSerialize = ['user']
Papers._meta._virtualfields = ['lab','species','factors']

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
    def upload_factory(sub_dir):
        """a factory for generating upload_to_path fns--e.g. use to generate
        the various sub-directories we use to store the info associated w/
        a sample"""
        def upload_to_path(self, filename):
            """Returns the upload_to path for this dataset.
            NOTE: we are going to store the files by gsmid, e.g. GSM566957
            is going to be stored in: data/datasets/gsm566/957.
            I'm not sure if this is the place to validate gsmids, but it maybe
            """
            return os.path.join('data', 'datasets','gsm%s' % self.gsmid[3:6],
                                self.gsmid[6:], sub_dir, filename)
        return upload_to_path

    #def __init__(self, *args):
    #    super(Datasets, self).__init__(*args)
    #    self._meta._donotSerialize = ['user']
    
    gsmid = models.CharField(max_length=255, null=True, blank=True, default="")
    #Name comes from "title" in the geo sample information
    name = models.CharField(max_length=255, null=True, blank=True, default="")
    chip_page = models.URLField(null=True, blank=True, default="")
    control_gsmid = models.CharField(max_length=255, null=True, blank=True, 
                                     default="")
    control_page = models.URLField(null=True, blank=True, default="")
    date_collected = models.DateTimeField(null=True, blank=True, default=None)
    #FILES--maybe these should be in a different table, but for now here they r
    raw_file = models.FileField(upload_to=upload_factory("raw"),
                                null=True, blank=True)
    raw_file_url = models.URLField(max_length=255,
                                   null=True, blank=True)
    raw_file_type = models.ForeignKey('FileTypes',
                                      null=True, blank=True, default=None)
    treatment_file = models.FileField(upload_to=upload_factory("treatment"),
                                      null=True, blank=True)
    peak_file = models.FileField(upload_to=upload_factory("peak"),
                                 null=True, blank=True)
    wig_file = models.FileField(upload_to=upload_factory("wig"),
                                null=True, blank=True)
    bw_file = models.FileField(upload_to=upload_factory("bw"),
                                null=True, blank=True)
    
    #IF everything is done by auto import we might not need this
    user = models.ForeignKey(User, null=True, blank=True, default=None)
    paper = models.ForeignKey('Papers', null=True, blank=True, default=None)
    #BONZAI! moving this meta info to samples, soon to be renamed datasets
    # factor = models.ForeignKey('Factors', null=True, blank=True, default=None)

    # platform = models.ForeignKey('Platforms',
    #                              null=True, blank=True, default=None)
    # species = models.ForeignKey('Species',
    #                             null=True, blank=True, default=None)
    # assembly = models.ForeignKey('Assemblies',
    #                              null=True, blank=True, default=None)
    # # #in description, we can add additional info e.g. protocols etc
    # description = models.TextField(blank=True)
    # cell_type = models.ForeignKey('CellTypes',
    #                               null=True, blank=True, default=None)
    # cell_line = models.ForeignKey('CellLines',
    #                               null=True, blank=True, default=None)
    # cell_pop = models.ForeignKey('CellPops',
    #                              null=True, blank=True, default=None)
    # strain = models.ForeignKey('Strains',
    #                            null=True, blank=True, default=None)
    # condition = models.ForeignKey('Conditions',
    #                               null=True, blank=True, default=None)

    # disease_state = models.ForeignKey('DiseaseStates',
    #                                   null=True, blank=True, default=None)
    
    status = models.CharField(max_length=255, choices=DATASET_STATUS,
                              default="imported")
    comments = models.TextField(blank=True)
    
    #user = the person who created this dataset (paper team)
    #uploader = the person who uploaded the files (data team)
    uploader = models.ForeignKey(User, null=True, blank=True, default=None,
                                 related_name="uploader")
    upload_date = models.DateTimeField(blank=True, null=True, default=None)
    
    #curator = the person who double checks the info
    curator = models.ForeignKey(User, null=True, blank=True, default=None,
                                related_name="curator")
    
Datasets._meta._donotSerialize = ['user', 'uploader', 'curator']

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
    experiment_type = models.CharField(max_length=10, blank=True,
                                       choices=EXPERIMENT_TYPE_CHOICES)
                                       
    def __str__(self):
        return self.name


class Factors(DCModel):
    """The factors applied to the sample, e.g. PolII, H3K36me3, etc."""
    name = models.CharField(max_length=255)
    antibody = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=255, choices=FACTOR_TYPES,
                            default="other")
    def __str__(self):
        if self.antibody:
            return "%s:%s" % (self.name, self.antibody)
        else:
            return self.name

class CellTypes(DCModel):
    """Sample's tissue/cell type, e.g. embryonic stem cell, b lymphocytes, etc.
    """
    name = models.CharField(max_length=255)
    tissue_type = models.CharField(max_length=255, blank=True)
    def __str__(self):
        if self.tissue_type:
            return "%s:%s" % (self.name, self.tissue_type)
        else:
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
        return smart_str(self.name)

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
    user = models.ForeignKey(User, null=True, blank=True, default=None) 
    ip_addr = models.CharField(max_length=15)
    submitter_name = models.CharField(max_length=255, blank=True)
    comments = models.TextField(blank=True)

PaperSubmissions._meta._donotSerialize = ['user']

class FileTypes(DCModel):
    """File types for our geo datasets"""
    name = models.CharField(max_length=20)
    def __str__(self):
        return self.name

class Species(DCModel):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name
    
class Assemblies(DCModel):
    name = models.CharField(max_length=255)
    pub_date = models.DateField(blank=True)
    def __str__(self):
        return self.name

class Samples(DCModel):
    """a table to store all of the sample information: a sample is a
    set of one or more datasets; it is associated with a paper (one paper to
    many samples)"""
    def upload_factory(sub_dir):
        """a factory for generating upload_to_path fns--e.g. use to generate
        the various sub-directories we use to store the info associated w/
        a sample"""
        def upload_to_path(self, filename):
            """Returns the upload_to path for this sample.
            NOTE: we are going to store the files by the paper's gseid and
            the sample id, e.g. gseid = GSE20852, sample id = 578
            is going to be stored in: data/samples/gse20/852/578/[peak,wig,etc]
            """
            return os.path.join('data', 'samples',
                                'gse%s' % self.paper.gseid[3:5],
                                self.paper.gseid[5:], str(self.id), sub_dir,
                                filename)
        return upload_to_path
    
    user = models.ForeignKey(User)
    paper = models.ForeignKey('Papers')
    #DROPPING datasets in favor of a more robust way of defining which 
    #datasets.
    treatments = models.CommaSeparatedIntegerField(max_length=255, null=True,
                                                   blank=True)
    controls = models.CommaSeparatedIntegerField(max_length=255, null=True,
                                                 blank=True)
    #FileFields
    treatment_file = models.FileField(upload_to=upload_factory("treatment"),
                                      null=True, blank=True)
    peak_file = models.FileField(upload_to=upload_factory("peak"),
                                 null=True, blank=True)
    peak_xls_file = models.FileField(upload_to=upload_factory("peak"),
                                     null=True, blank=True)
    summit_file = models.FileField(upload_to=upload_factory("summit"),
                                   null=True, blank=True)
    wig_file = models.FileField(upload_to=upload_factory("wig"),
                                null=True, blank=True)
    #control_wig_file = models.FileField(upload_to=upload_factory("wig"),
    #                                    null=True, blank=True)
    bw_file = models.FileField(upload_to=upload_factory("bw"),
                                null=True, blank=True)
    bed_graph_file = models.FileField(upload_to=upload_factory("bedgraph"),
                                      null=True, blank=True)
    control_bed_graph_file = models.FileField(upload_to=upload_factory("bedgraph"),
                                              null=True, blank=True)
    conservation_file = models.FileField(upload_to=upload_factory("conservation"),
                                    null=True, blank=True)
    conservation_r_file = models.FileField(upload_to=upload_factory("conservation"),
                                      null=True, blank=True)
    qc_file = models.FileField(upload_to=upload_factory("qc"),
                               null=True, blank=True)
    qc_r_file = models.FileField(upload_to=upload_factory("qc"),
                                 null=True, blank=True)
    ceas_file = models.FileField(upload_to=upload_factory("ceas"),
                                 null=True, blank=True)
    ceas_r_file = models.FileField(upload_to=upload_factory("ceas"),
                                   null=True, blank=True)
    venn_file = models.FileField(upload_to=upload_factory("venn"),
                                 null=True, blank=True)
    seqpos_file = models.FileField(upload_to=upload_factory("seqpos"),
                                   null=True, blank=True)

    #adding meta files
    conf_file = models.FileField(upload_to=upload_factory("meta"),
                                 null=True, blank=True)
    log_file = models.FileField(upload_to=upload_factory("meta"),
                                 null=True, blank=True)
    summary_file = models.FileField(upload_to=upload_factory("meta"),
                                    null=True, blank=True)
    #NOTE: even though dhs stats are saved in a table, we're going to store it
    #in meta
    dhs_file = models.FileField(upload_to=upload_factory("meta"),
                                null=True, blank=True)

    #uploader = the person who uploaded the files (data team)
    uploader = models.ForeignKey(User, null=True, blank=True, default=None,
                                 related_name="sample_uploader")
    upload_date = models.DateTimeField(blank=True, null=True, default=None)

    #meta info
    factor = models.ForeignKey('Factors', null=True, blank=True, default=None)

    platform = models.ForeignKey('Platforms',
                                 null=True, blank=True, default=None)
    species = models.ForeignKey('Species',
                                null=True, blank=True, default=None)
    assembly = models.ForeignKey('Assemblies',
                                 null=True, blank=True, default=None)
    #in description, we can add additional info e.g. protocols etc
    description = models.TextField(null=True, blank=True, default="")
    cell_type = models.ForeignKey('CellTypes',
                                  null=True, blank=True, default=None)
    cell_line = models.ForeignKey('CellLines',
                                  null=True, blank=True, default=None)
    cell_pop = models.ForeignKey('CellPops',
                                 null=True, blank=True, default=None)
    strain = models.ForeignKey('Strains',
                               null=True, blank=True, default=None)
    condition = models.ForeignKey('Conditions',
                                  null=True, blank=True, default=None)
    disease_state = models.ForeignKey('DiseaseStates',
                                      null=True, blank=True, default=None)
    #end meta info

    status = models.CharField(max_length=255, choices=SAMPLE_STATUS,
                              null=True, blank=True, default="new")

    comments = models.TextField(null=True, blank=True, default="")


    def _printInfo(self):
        """Tries to print the treatment and controls list like this:
        GSMXXX,GSMYYY::GSMZZZ where the :: is a separator btwn the two lists"""
        treat = []
        control = []
        if self.treatments:
            treat = [Datasets.objects.get(id=d) \
                         for d in self.treatments.split(',')]
        if self.controls:
            controls = [Datasets.objects.get(id=d) \
                         for d in self.controls.split(',')]
        return "%s::%s" % (",".join(treat), ",".join(control))

    def __str__(self):
        #return self._printInfo()
        return str(self.id)
Samples._meta._donotSerialize = ['user', 'uploader']

class SampleControls(DCModel):
    """a table to store all of the control files for a given sample.
    The replicates of each sample uses the same control--so this is the
    central repository.
    """
    def upload_factory(sub_dir):
        """a factory for generating upload_to_path fns--e.g. use to generate
        the various sub-directories we use to store the info associated w/
        a samplecontrol"""
        def upload_to_path(self, filename):
            """Returns the upload_to path for this sample.
            NOTE: we are going to store the files by the paper's gseid and
            the sample id, e.g. gseid = GSE20852, sample id = 578
            is going to be stored in:data/controls/gse20/852/578/[peak,wig,etc]
            """
            return os.path.join('data', 'controls','gse%s' % \
                                self.sample.paper.gseid[3:5],
                                self.sample.paper.gseid[5:],
                                str(self.sample.id), sub_dir, filename)
        return upload_to_path
    
    sample = models.ForeignKey('Samples')
    treatment_file = models.FileField(upload_to=upload_factory("treatment"),
                                      null=True, blank=True)
    wig_file = models.FileField(upload_to=upload_factory("wig"),
                                null=True, blank=True)
    bw_file = models.FileField(upload_to=upload_factory("bw"),
                               null=True, blank=True)
    
class UserProfiles(DCModel):
    """We want to add additional fields to the auth user model.  So creating
    this UserProfile model is the django way of doing it.
    ref: http://scottbarnham.com/blog/2008/08/21/extending-the-django-user-model-with-inheritance/
    NOTE: in the ref, the guy explains how to do it through model inheritance,
    but get_profile is now a django idiom that i decided to use it instead.
    """
    user = models.ForeignKey(User, unique=True, related_name='profile')
    #which team is the user on, paper team or data team
    team = models.CharField(max_length=255, choices=TEAMS, blank=True,
                            null=True, default=None)
#UserProfiles._meta._donotSerialize = ['user']

    
class DiseaseStates(DCModel):
    """Information field for datasets"""
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)

class SampleDhsStats(DCModel):
    """Stats about the sample"""
    sample = models.ForeignKey('Samples', unique=True)
    total_peaks = models.IntegerField(default=0)
    peaks_in_dhs = models.IntegerField(default=0)
