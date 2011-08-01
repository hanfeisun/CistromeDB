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
    (u'imported', u'paper entered awaiting samples'),
    (u'primed', u'samples imported awaiting download'),
    (u'transfer', u'samples download in progress'),
    (u'downloaded', u'samples downloaded awaiting analysis'),
    (u'complete', u'analysis complete/complete'),
    (u'error', u'error/hold- see comments'),
    )

SAMPLE_STATUS = (
    (u'imported', u'imported awaiting meta-info'),
    (u'info', u'meta-info inputted awaiting validation'),
    (u'valid', u'meta-info validated awaiting file download'),
    (u'transfer', u'file is downloading'),
    (u'downloaded', u'downloaded/closed'),
    (u'error', u'error/hold- see comments'),
    )

DATASET_STATUS = (
    (u'new', u'dataset created, awaiting check for raw files'),
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

GRADE_CHOICES = (
    (u'A', u'A'),
    (u'B', u'B'),
    (u'C', u'C'),
    (u'D', u'D'),
    )

QC_CHOICES = (
    (u'PASS', u'PASS'),
    (u'FAIL', u'FAIL'),
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
    generic_id = models.CharField(max_length=255, null=True, blank=True, 
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
                              null=True, blank=True, default="imported")
    #a place for curators to add comments
    comments = models.TextField(null=True, blank=True, default="")

    def _get_species(self):
        """Returns a list of the species objs associated with the papers, i.e.
        the set of species that are found in the paper's datasets"""
        tmp = []
        datasets = Datasets.objects.filter(paper=self.id)
        for d in datasets:
            if d.species and d.species.name not in tmp:
                tmp.append(smart_str(d.species.name))
        return tmp

    def _get_factors(self):
        """Returns a list of the factors associated w/ the paper, i.e.
        returns the set of factors that are found in the paper's datasets"""
        tmp = []
        datasets = Datasets.objects.filter(paper=self.id)
        for d in datasets:
            if d.factor and d.factor.name not in tmp:
                tmp.append(smart_str(d.factor.name))
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

#class Datasets(DCModel):
class Samples(DCModel):
    """!!DEPRECATED DOC!! PLEASE UPDATE ME!
    """
    def upload_factory(sub_dir):
        """a factory for generating upload_to_path fns--e.g. use to generate
        the various sub-directories we use to store the info associated w/
        a sample"""
        def upload_to_path(self, filename):
            """Returns the upload_to path for this sample.
            NOTE: we are going to store the files by gsmid, e.g. GSM566957
            is going to be stored in: data/samples/gsm566/957.
            I'm not sure if this is the place to validate gsmids, but it maybe
            """
            return os.path.join('data', 'samples','gsm%s' % self.gsmid[3:6],
                                self.gsmid[6:], sub_dir, filename)
        return upload_to_path
    
    gsmid = models.CharField(max_length=255, null=True, blank=True, default="")
    generic_id = models.CharField(max_length=255, null=True, blank=True,
                                  default="")
    #Name comes from "title" in the geo sample information
    name = models.CharField(max_length=255, null=True, blank=True, default="")
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
    
    status = models.CharField(max_length=255, choices=SAMPLE_STATUS,
                              null=True, blank=True, default="imported")
    comments = models.TextField(null=True, blank=True, default="")
    
    uploader = models.ForeignKey(User, null=True, blank=True, default=None,
                                 related_name="uploader")
    upload_date = models.DateTimeField(blank=True, null=True, default=None)
    
    #curator = the person who double checks the info
    curator = models.ForeignKey(User, null=True, blank=True, default=None,
                                related_name="curator")
    def __str__(self):
        return str(self.id)
    
Samples._meta._donotSerialize = ['user', 'uploader', 'curator']

#class Samples(DCModel):
class Datasets(DCModel):
    """a table to store all of the dataset information: a dataset is a
    set of one or more samples; it is associated with a paper (one paper to
    many datasets)"""
    def upload_factory(sub_dir):
        """a factory for generating upload_to_path fns--e.g. use to generate
        the various sub-directories we use to store the info associated w/
        a sample"""
        def upload_to_path(self, filename):
            """Returns the upload_to path for this dataset.
            NOTE: we are going to store the files by the paper's gseid and
            the sample id, e.g. gseid = GSE20852, dataset id = 578
            is going to be stored in: data/datasets/gse20/852/578/[peak,wig,etc]
            """
            return os.path.join('data', 'datasets',
                                'gse%s' % self.paper.gseid[3:5],
                                self.paper.gseid[5:], str(self.id), sub_dir,
                                filename)
        return upload_to_path
    
    user = models.ForeignKey(User)
    paper = models.ForeignKey('Papers')
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
                                 related_name="dataset_uploader")
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
    chip_page = models.URLField(null=True, blank=True, default="")
    control_page = models.URLField(null=True, blank=True, default="")
    #end meta info

    status = models.CharField(max_length=255, choices=DATASET_STATUS,
                              null=True, blank=True, default="new")

    comments = models.TextField(null=True, blank=True, default="")

    #QC fields
    read_qc = models.CharField(max_length=255, choices=QC_CHOICES,
                               null=True, blank=True, default=None)
    model_qc = models.CharField(max_length=255, choices=QC_CHOICES,
                                null=True, blank=True, default=None)
    fold_qc = models.CharField(max_length=255, choices=QC_CHOICES,
                               null=True, blank=True, default=None)
    fdr_qc = models.CharField(max_length=255, choices=QC_CHOICES,
                              null=True, blank=True, default=None)
    replicate_qc = models.CharField(max_length=255, choices=QC_CHOICES,
                                    null=True, blank=True, default=None)
    dnase_qc = models.CharField(max_length=255, choices=QC_CHOICES,
                                null=True, blank=True, default=None)
    velcro_qc = models.CharField(max_length=255, choices=QC_CHOICES,
                                 null=True, blank=True, default=None)
    conserve_qc = models.CharField(max_length=255, choices=QC_CHOICES,
                                  null=True, blank=True, default=None)
    ceas_qc = models.CharField(max_length=255, choices=QC_CHOICES,
                               null=True, blank=True, default=None)
    motif_qc = models.CharField(max_length=255, choices=QC_CHOICES,
                               null=True, blank=True, default=None)
    overall_qc = models.CharField(max_length=255, choices=GRADE_CHOICES,
                                  null=True, blank=True, default=None)

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
Datasets._meta._donotSerialize = ['user', 'uploader']

#NOTE: WE NEED TO RENAME THIS!! and create a table!
class Controls(DCModel):
    """a table to store all of the control files for a given dataset.
    The replicates of each dataset uses the same control--so this is the
    central repository.
    """
    def upload_factory(sub_dir):
        """a factory for generating upload_to_path fns--e.g. use to generate
        the various sub-directories we use to store the info associated w/
        a control"""
        def upload_to_path(self, filename):
            """Returns the upload_to path for this control.
            NOTE: we are going to store the files by the paper's gseid and
            the dataset id, e.g. gseid = GSE20852, dataset id = 578
            is going to be stored in:data/controls/gse20/852/578/[peak,wig,etc]
            """
            return os.path.join('data', 'controls','gse%s' % \
                                self.dataset.paper.gseid[3:5],
                                self.dataset.paper.gseid[5:],
                                str(self.dataset.id), sub_dir, filename)
        return upload_to_path
    
    dataset = models.ForeignKey('Datasets', related_name="controls_dataset")
    treatment_file = models.FileField(upload_to=upload_factory("treatment"),
                                      null=True, blank=True)
    wig_file = models.FileField(upload_to=upload_factory("wig"),
                                null=True, blank=True)
    bw_file = models.FileField(upload_to=upload_factory("bw"),
                               null=True, blank=True)

class Platforms(DCModel):
    """Platforms are the chips/assemblies used.
    For example, it can be an Affymetrix Human Genome U133 Plus 2.0 Array,
    i.e. GPLID = GPL570
    The fields are:
    name- name of the platform
    gplid - GEO Platform ID
    experiment type- Choice: ChIP-Chip/ChIP-Seq
    """
    gplid = models.CharField(max_length=7, null=True, blank=True, default="")
    generic_id = models.CharField(max_length=255, null=True, blank=True, 
                                  default="")
    name = models.CharField(max_length=255, blank=True)
    technology = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    experiment_type = models.CharField(max_length=10, blank=True,
                                       choices=EXPERIMENT_TYPE_CHOICES)
                                       
    def __str__(self):
        return self.name


class Factors(DCModel):
    """The factors applied e.g. PolII, H3K36me3, etc.
    """
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
    """tissue/cell type, e.g. embryonic stem cell, b lymphocytes, etc.
    """
    name = models.CharField(max_length=255)
    tissue_type = models.CharField(max_length=255, blank=True)
    def __str__(self):
        if self.tissue_type:
            return "%s:%s" % (self.name, self.tissue_type)
        else:
            return self.name

class CellLines(DCModel):
    """cell lines.  I really don't know what distinguishes
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
    """Experiment/conditions, e.g. PTIP-knockout, wild-type"""
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
    status = models.CharField(max_length=255, choices=SUBMISSION_STATUS,
                              null=True, blank=True, default="pending")
    user = models.ForeignKey(User, null=True, blank=True, default=None) 
    ip_addr = models.CharField(max_length=15)
    submitter_name = models.CharField(max_length=255, blank=True)
    comments = models.TextField(blank=True)

PaperSubmissions._meta._donotSerialize = ['user']

class FileTypes(DCModel):
    """File types for our geo datasets
    """
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
    """Disease state meta info"""
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)

class DhsStats(DCModel):
    """Stats about the sample"""
    dataset = models.ForeignKey('Datasets', unique=True)
    total_peaks = models.IntegerField(default=0)
    peaks_in_dhs = models.IntegerField(default=0)
