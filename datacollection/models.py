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
    """Papers are publications that are publicly available
    The fields are:
    pmid - the pubmed id of the publication
    unique_id - the unique identifier for an external db, e.g. GSEID
    user - the user who currated the dataset
    title - the title of the publication
    reference - shorthand of the publication details
    abstract - the abstract of the publication
    pub_date - the publication date
    authors - list of the paper's authors
    last_aut_email - the email address of the last/corresponding author
    journal- paper's journal

    status- SEE PAPER_STATUS above
    comments- any comments about this paper
    """
    #def __init__(self, *args):
    #    super(Papers, self).__init__(*args)
    #    self._meta._donotSerialize = ['user']

    pmid = models.IntegerField(null=True, blank=True, default=None)
    #NOTE: papers can have multiple unique_ids attached--if so, comma-sep them
    unique_id = models.CharField(max_length=255, null=True, blank=True, default="")
    user = models.ForeignKey(User, null=True, blank=True, default=None)
    title = models.CharField(max_length=255, null=True, blank=True, default="")
    reference = models.CharField(max_length=255, null=True, blank=True, default="")
    abstract = models.TextField(null=True, blank=True, default="")
    pub_date = models.DateField(null=True, blank=True, default=None)
    date_collected = models.DateTimeField(null=True, blank=True, default=None)
    authors = models.CharField(max_length=255, null=True,blank=True,default="")
    last_auth_email = models.EmailField(null=True, blank=True, default=None)
        
    journal = models.ForeignKey('Journals',
                                null=True, blank=True, default=None)
    status = models.CharField(max_length=255, choices=PAPER_STATUS,
                              null=True, blank=True, default="imported")
    #a place for curators to add comments
    comments = models.TextField(null=True, blank=True, default="")

    #MIG_NOTE: these will have to change from DATASET --> SAMPLE
    # def _datasetAggregator(dset_field):
    #     """Given a dataset field, tries to aggregate all of the associated 
    #     datasets"""
    #     #pluralizing the dset_field
    #     #exceptions first
    #     if dset_field == 'species':
    #         plural = 'species'
    #     elif dset_field == 'assembly':
    #         plural = 'assemblies'
    #     else:
    #         plural = dset_field+'s'

    #     def nameless(self):
    #         "Returns a list of %s associates with the papers" % plural
    #         ids = []
    #         vals = []
    #         dsets = Datasets.objects.filter(paper=self.id)
    #         for d in dsets:
    #             val = getattr(d, dset_field)
    #             if val and val.id not in ids:
    #                 ids.append(val.id)
    #                 vals.append(smart_str(val))
    #         return vals
    #     return nameless

    
    # factors = property(_datasetAggregator('factor'))
    # platforms = property(_datasetAggregator('platform'))
    # species = property(_datasetAggregator('species'))
    # assemblies = property(_datasetAggregator('assembly'))
    # cell_types = property(_datasetAggregator('cell_type'))
    # cell_lines = property(_datasetAggregator('cell_line'))
    # cell_pops = property(_datasetAggregator('cell_pop'))
    # tissue_types = property(_datasetAggregator('tissue_type'))
    # strains = property(_datasetAggregator('strain'))
    # conditions = property(_datasetAggregator('condition'))
    # disease_states = property(_datasetAggregator('disease_state'))

    # def _aggGSMIDS(self):
    #     dsets = Datasets.objects.filter(paper=self.id)
    #     #NOTE: we are wrapping up the gsmid and the associated factor!
    #     return [[smart_str(d.gsmid), smart_str(d.factor), smart_str(d.generic_id)] for d in dsets]

    # gsmids = property(_aggGSMIDS)

    def _get_lab(self):
        """Returns the last author in the authors list"""
        try:
            return smart_str(self.authors.split(",")[-1:][0])
        except:
            return smart_str(self.authors)

    lab = property(_get_lab)
    
    def __str__(self):
        return smart_str(self.title)

#NOTE: _donotSerialize fields are not enumerated as records, just as keys
Papers._meta._donotSerialize = ['user']

#Dataset fields which we will aggregate and make into virtual paper fields
Papers._meta._virtualfields = ['lab', #'factors', 'platforms', 'species', 
                               #'assemblies', 'cell_types', 'cell_lines', 
                               #'cell_pops', 'tissue_types', 'strains', 
                               #'conditions', 'disease_states', 'gsmids'
                               ]


class Datasets(DCModel):
    """Datasets are SETS of samples, typically a set (1 or more) of treatment
    samples and a set (0 or more) of control samples.

    **They are the HIGHER-level representations; samples are the lower-level.

    Dataset fields:
    user_id - the user who currated the dataset
    paper_id - the paper that the dataset is associated with

    [Virtual fields- meta data inferred from treatment (and sometimes 
    control) samples]
    [File fields]
    peak_bed
    peak_wig
    ...etc..
    """

    #MIG_NOTE: CAN'T depend on GSMIDS
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

    #user = the person curated/created the dataset
    user = models.ForeignKey(User, null=True, blank=True, default=None)
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

    date_created = models.DateTimeField(blank=True, null=True, default=None)

    status = models.CharField(max_length=255, choices=DATASET_STATUS,
                              default="new")

    comments = models.TextField(blank=True, default="")

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
    
Datasets._meta._donotSerialize = ['user']

class Samples(DCModel):
    """a table to store all of the sample information: a sample is a
    set of one or more datasets; it is associated with a paper (one paper to
    many samples)"""

    #MIG_NOTE: can't rely on GSE!
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

    #user = curator/uploader of this sample
    user = models.ForeignKey(User, null=True, blank=True, default=None)
    paper = models.ForeignKey('Papers', null=True, blank=True, default=None)
    
    unique_id = models.CharField(max_length=255, null=True, blank=True, default="")
    #Name comes from "title" in the geo sample information
    name = models.CharField(max_length=255, null=True, blank=True, default="")
    date_collected = models.DateTimeField(null=True, blank=True, default=None)

    #RAW FILES assoc. w/ sample--i.e. FASTQ, and then when aligned --> BAM;
    #DELETE fastq when bam is generated
    fastq_file = models.FileField(upload_to=upload_factory("fastq"),
                                null=True, blank=True)
    fastq_file_url = models.URLField(max_length=255,
                                   null=True, blank=True)
    bam_file = models.FileField(upload_to=upload_factory("bam"),
                                      null=True, blank=True)
    
    #META information
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
    tissue_type = models.ForeignKey('TissueTypes', null=True, blank=True, 
                                    default=None)
    antibody = models.ForeignKey('Antibodies', null=True, blank=True, 
                                 default=None)

    #curator = the person who double checks the info
    curator = models.ForeignKey(User, null=True, blank=True, default=None,
                                related_name="curator")

    status = models.CharField(max_length=255, choices=SAMPLE_STATUS,
                              null=True, blank=True, default="imported")
    comments = models.TextField(null=True, blank=True, default="")
    
    upload_date = models.DateTimeField(blank=True, null=True, default=None)


    def __str__(self):
        #return self._printInfo()
        return smart_str(str(self.id))

Samples._meta._donotSerialize = ['user', 'curator']

class Platforms(DCModel):
    """Platforms are the chips/assemblies used to generate the dataset.
    For example, it can be an Affymetrix Human Genome U133 Plus 2.0 Array,
    i.e. GPLID = GPL570
    The fields are:
    name- name of the platform
    gplid - GEO Platform ID
    experiment type- Choice: ChIP-Chip/ChIP-Seq
    """
    gplid = models.CharField(max_length=255, null=True, blank=True, default="")
    name = models.CharField(max_length=255, null=True, blank=True, default="")
    technology = models.CharField(max_length=255, null=True, blank=True, default="")
    company = models.CharField(max_length=255, null=True, blank=True, default="")
    experiment_type = models.CharField(max_length=10, null=True, blank=True,
                                       default="",
                                       choices=EXPERIMENT_TYPE_CHOICES)
                                       
    def __str__(self):
        return smart_str(self.name)


class Factors(DCModel):
    """The factors applied to the sample, e.g. PolII, H3K36me3, etc."""
    name = models.CharField(max_length=255)
    #antibody = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=255, choices=FACTOR_TYPES,
                            default="other")
    def __str__(self):
        return smart_str(self.name)

class CellTypes(DCModel):
    """Sample's tissue/cell type, e.g. embryonic stem cell, b lymphocytes, etc.
    """
    name = models.CharField(max_length=255)
    #tissue_type = models.CharField(max_length=255, blank=True)
    def __str__(self):
        return smart_str(self.name)

class CellLines(DCModel):
    """Sample's cell lines.  I really don't know what distinguishes
    cell lines from cell populations or strains and mutations, but i'm going
    to create the tables just to be inclusive
    """
    name = models.CharField(max_length=255)
    def __str__(self):
        return smart_str(self.name)

class CellPops(DCModel):
    name = models.CharField(max_length=255)
    def __str__(self):
        return smart_str(self.name)

class Strains(DCModel):
    name = models.CharField(max_length=255)
    def __str__(self):
        return smart_str(self.name)
    
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
        return smart_str(self.name)

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
    #MIG_NOTE: need to change gseid to maybe unique_id or add something for 
    #SRA/ENCODE etc
    pmid = models.IntegerField(default=0)
    gseid = models.CharField(max_length=8, blank=True)
    status = models.CharField(max_length=255, choices=SUBMISSION_STATUS)
    user = models.ForeignKey(User, null=True, blank=True, default=None) 
    ip_addr = models.CharField(max_length=15)
    submitter_name = models.CharField(max_length=255, blank=True)
    comments = models.TextField(blank=True)

PaperSubmissions._meta._donotSerialize = ['user']

class Species(DCModel):
    name = models.CharField(max_length=255)
    def __str__(self):
        return smart_str(self.name)
    
class Assemblies(DCModel):
    name = models.CharField(max_length=255)
    pub_date = models.DateField(blank=True)
    def __str__(self):
        return smart_str(self.name)
    
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
        return smart_str(str(self.name))

class Antibodies(DCModel):
    """Antibodies"""
    name = models.CharField(max_length=255)
    def __str__(self):
        return smart_str(self.name)

class TissueTypes(DCModel):
    """Tissue Types"""
    name = models.CharField(max_length=255)
    def __str__(self):
        return smart_str(self.name)

# class SampleDhsStats(DCModel):
#     """Stats about the sample"""
#     sample = models.ForeignKey('Samples', unique=True)
#     total_peaks = models.IntegerField(default=0)
#     peaks_in_dhs = models.IntegerField(default=0)
