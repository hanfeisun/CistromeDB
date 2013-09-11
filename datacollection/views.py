import os
import sys
import datetime
import subprocess
import re
#import daemon

from django.shortcuts import render_to_response, Http404, get_object_or_404
from django.contrib import auth
from django.template import RequestContext
import django.contrib.auth.decorators as decorators
from django.views.decorators.cache import cache_page
from django.views.generic.simple import direct_to_template
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect, HttpResponse
#from django.contrib.auth.views import login
from django.core.urlresolvers import reverse
from django.db.models import Q, Count, Max, Min, Avg, query, manager
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.cache import cache
from django.utils.encoding import smart_str
from django.utils.http import urlquote
#unquote
#ref: http://stackoverflow.com/questions/5229054/django-urldecode-in-template-file
from urllib import unquote

from django.conf import settings as conf_settings
from django.db.models.fields.files import FileField

import models
import forms
import settings
import entrez
import jsrecord.views
import pipeline.ConfGenerator as ConfGenerator
import pipeline.RunSHGenerator as RunSHGenerator
import importer.DnldSHGenerator as DnldSHGenerator
from haystack.query import SearchQuerySet

try:
    import json
except ImportError:
    import simplejson as json

FIRST_PMID = 11125145

#a trick to get the current module
_modname = globals()['__name__']
_this_mod = sys.modules[_modname]
_datePattern = "^\d{4}-\d{1,2}-\d{1,2}$"
_items_per_page = 25
#when the oldest/newest paper was published
_dateRange = models.Papers.objects.aggregate(Min('pub_date'),Max('pub_date'))


_sidebarPages = ['home', 'paper_submission', 'dcstats', 'help', 'contact']
#how they are printed on the page
_sidebarNames = ["Home", 'Submit a Paper', "Collection Stats", "Help", 'Contact Us']

_adminSidebar = [('datasets', 'Datasets'), 
                 ('samples', 'Samples'), 
                 ('papers', 'Papers'), 
                 ('fieldsView', 'Fields'),
                 ]


def admin_only(function=None):
    """
    Decorator for views that checks that the user is logged in AND is_staff.
    based closely on django.contrib.auth.decorators.login_required
    """
    def _dec(view_fn):
        def _view(request, *args, **kwargs):
            #check that user is logged in AND is_staff
            if request.user.is_authenticated() and request.user.is_staff:
                return view_fn(request, *args, **kwargs)
            elif not request.user.is_authenticated():
                #redirect to login
                path = urlquote(request.get_full_path())
                #tup = self.login_url, self.redirect_field_name, path
                tup = conf_settings.LOGIN_URL, auth.REDIRECT_FIELD_NAME, path
                return HttpResponseRedirect('%s?%s=%s' % tup)
                #return HttpResponseRedirect(auth.REDIRECT_FIELD_NAME)
            elif not request.user.is_staff:
                return direct_to_template(request, 
                                          "registration/restricted.html")
            else:
                #should never reach
                pass
        _view.__name__ = view_fn.__name__
        _view.__dict__ = view_fn.__dict__
        _view.__doc__ = view_fn.__doc__

        return _view
    if function:
        return _dec(function)
    return _dec

def no_view(request):
    """
    We don't really want anyone going to the static_root.
    However, since we're raising a 404, this allows flatpages middleware to
    step in and serve a page, if there is one defined for the URL.
    """
    raise Http404

def home(request):
    #show the 10 newest papers
    #NOTE: sidebarURLs can't be generated at the module level
    sidebarURLs = [reverse(p) for p in _sidebarPages]
    sidebar = zip(_sidebarPages, sidebarURLs, _sidebarNames)
    currpage = "home"

    papers = models.Papers.objects.order_by('-date_collected')[:10]
    factors = models.Factors.objects.all().extra(select={'upper_name':'upper(name)'}).order_by('upper_name');

    #build cells
    cells = []
    for (m, ann) in [(models.CellLines, "cl"), (models.CellPops, "cp"), 
                     (models.CellTypes, "ct"), (models.TissueTypes, "tt")]:
        tmp = [(ann, c) for c in m.objects.all()]
        cells.extend(tmp)
    cells = sorted(cells, key=lambda x: x[1].name.upper())

    #remove control factors
    _removeList = ['Control', 'gfp', 'IgG', 'RevXlinkChromatin', 'Input']
    factors = [f for f in factors if f.name not in _removeList]

    return render_to_response('datacollection/home.html', locals(),
                              context_instance=RequestContext(request))

@admin_only
def new_paper_form(request):
    #errors = []
    #NOTE: by convention i should have to do this; django should be smart
    #enough to scrape these fields for me if i leave them the same
    fields = ['pmid', 'gseid', 'title', 'abstract', 'pub_date',
              'last_auth', 'last_auth_email']
    form = None;
    if request.method == "POST":
        form = forms.PaperForm(request.POST)
        if form.is_valid():
            #tmp = form.save(commit=False) #will not commit to db
            #tmp = form.save() #will commit to the db
            tmp = form.save(commit=False)
            tmp.date_collected = datetime.datetime.now()
            tmp.user = request.user
            tmp.save()
            return HttpResponseRedirect(reverse('papers'))
    else:
        form = forms.PaperForm()
    return render_to_response('datacollection/new_paper_form.html', locals(),
                              context_instance=RequestContext(request))

#MIG_NOTE: Begin: may need to alter these
@admin_only
def new_dataset_form(request):
    if request.method == "POST":
        form = forms.DatasetForm(request.POST, request.FILES)
        if form.is_valid():
            tmp = form.save(commit=False)
            tmp.date_collected = datetime.datetime.now()
            tmp.user = request.user
            #I'm not sure why the form isn't finding paper in request.POST
            tmp.paper = models.Papers.objects.get(id=request.POST['paper'])
            tmp.save()
            return HttpResponseRedirect(request.POST['next'])
        else:
            print "INVALID DATASET FORM"
    else:
        form = forms.DatasetForm()
        #NOTE: we can't pass in the param as paper b/c when we post, it
        #clobbers the hidden input in our form
        if 'next' in request.GET:
            next = request.GET['next']
        if 'p' in request.GET:
            #paper = models.Papers.objects.get(id=request.GET['paper'])
            paper = request.GET['p']
    return render_to_response('datacollection/new_dataset_form.html', locals(),
                              context_instance=RequestContext(request))

@admin_only
def upload_dataset_form(request, dataset_id):
    """Given a dataset_id, generate or handle a form that will allow users
    to upload the files associated with it
    """
    if request.method == "POST":
        dset = models.Datasets.objects.get(pk=dataset_id)
        #we want to only update the record, not add a new one--hence instance
        form = forms.UploadDatasetForm(request.POST, request.FILES,
                                       instance=dset)
        if form.is_valid():
            tmp = form.save(commit=False)
            tmp.upload_date = datetime.datetime.now()
            tmp.uploader = request.user
            tmp.save()
            return HttpResponseRedirect(reverse('home'))
        else:
            print "INVALID UPLOAD DATASET FORM"
    else:
        form = forms.UploadDatasetForm()
    return render_to_response('datacollection/upload_dataset_form.html',
                              locals(),
                              context_instance=RequestContext(request))

@admin_only
def new_sample_form(request):
    if request.method == "POST":
        tmp = models.Samples()
        tmp.user = request.user
        tmp.treatments = request.POST['treatments']
        tmp.controls = request.POST['controls']
        tmp.paper = models.Papers.objects.get(id=request.POST['paper'])
        tmp.save()
        return HttpResponseRedirect(request.POST['next'])
    else:
        form = forms.SampleForm()
        if 'next' in request.GET:
            next = request.GET['next']
        if 'p' in request.GET:
            paper = request.GET['p']
    return render_to_response('datacollection/new_sample_form.html',
                              locals(),
                              context_instance=RequestContext(request))
#MIG_NOTE: END: may need to alter these
#------------------------------------------------------------------------------
#GENERIC FORMS section
def form_view_factory(title_in, form_class):
    def generic_form_view(request):
        title = title_in
        if request.method == "POST":
            form = form_class(request.POST)
            if form.is_valid():
                tmp = form.save()
                return HttpResponseRedirect(request.POST['next'])
        else:
            form = form_class()
            if 'next' in request.GET:
                next = request.GET['next']
        return render_to_response('datacollection/generic_form.html', locals(),
                                  context_instance=RequestContext(request))
    return admin_only(generic_form_view)

#Cool! but we need the decorators!
generic_forms_list = ['platform','factor','celltype','cellline', 'cellpop',
                      'strain', 'condition', 'journal', 'species', 
                      'assembly', "diseasestate", "tissuetype"]
#new_platform_form = form_view_factory('Platform Form', forms.PlatformForm)
#Generate the generic form views
for name in generic_forms_list:
    form = getattr(forms, "%sForm" % name.capitalize())
    tmp_view = form_view_factory('%s Form' % name.capitalize(), form)
    setattr(_this_mod, "new_%s_form" % name.lower(), tmp_view)

#Generic Update section; does not work w/ FILE upload!--i.e. datasets and
#replicates model
def update_form_factory(title_in, form_class):
    def generic_update_view(request, id):
        title = title_in
        if request.method == "POST":
            #Should use get_object_or_404
            #tmp = get_object_or_404(form_class.Meta.model, id)
            tmp = form_class.Meta.model.objects.get(pk=id)
            form = form_class(request.POST, instance=tmp)
            if form.is_valid():
                tmp2 = form.save()
                return HttpResponseRedirect(request.POST['next'])
        else:
            #tmp = get_object_or_404(form_class.Meta.model, id)
            tmp = form_class.Meta.model.objects.get(pk=id)
            form = form_class(instance=tmp)
            if 'next' in request.GET:
                next = request.GET['next']
        return render_to_response('datacollection/generic_form.html', locals(),
                                  context_instance=RequestContext(request))
    return admin_only(generic_update_view)

#add papers,
generic_update_list = generic_forms_list + ['paper', 'sample', 'dataset']
for name in generic_update_list:
    form = getattr(forms, "%sForm" % name.capitalize())
    tmp_view = update_form_factory('%s Update Form' % name.capitalize(), form)
    setattr(_this_mod, "update_%s_form" % name.lower(), tmp_view)

#OVERRIDE the generated views
update_paper_form = update_form_factory('Paper Update Form',
                                          forms.UpdatePaperForm)
update_dataset_form = update_form_factory('Dataset Update Form',
                                          forms.UpdateDatasetForm)
update_sample_form = update_form_factory('Sample Update Form',
                                          forms.UpdateSampleForm)
#------------------------------------------------------------------------------
#The main views-

@admin_only
def papers(request, user_id):
    """If given a user_id, shows all of the papers imported by the user,
    otherwise shows all papers in the db"""
    #unzip _adminSidebar
    adminSidebar, adminSidebarNames = zip(*_adminSidebar)
    sidebarURLs = [reverse(p) for p in adminSidebar]
    sidebar = zip(adminSidebar, sidebarURLs, adminSidebarNames)
    currpage = "papers"

    if user_id:
        #NOTE: the current url regex doesn't parse out the / from the user_id
        if user_id.endswith("/"):
            user_id = user_id[:-1]
        papers = models.Papers.objects.filter(user=user_id)
    else:
        papers = models.Papers.objects.all()

    #control things w/ paginator
    #ref: http://docs.djangoproject.com/en/1.1/topics/pagination/
    paginator = Paginator(papers, _items_per_page) #25 dataset per page
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        pg = paginator.page(page)
    except (EmptyPage, InvalidPage):
        pg = paginator.page(paginator.num_pages)

    return render_to_response('datacollection/papers.html', locals(),
                              context_instance=RequestContext(request))

@admin_only
def datasets(request):
    """Returns all of the datasets
    """
    #unzip _adminSidebar
    adminSidebar, adminSidebarNames = zip(*_adminSidebar)
    sidebarURLs = [reverse(p) for p in adminSidebar]
    sidebar = zip(adminSidebar, sidebarURLs, adminSidebarNames)
    currpage = "datasets"

    fields = [f.name for f in models.Datasets._meta.fields]
    fields.insert(1, "conts")
    fields.insert(1, "treats")

    fileFields = [f.name for f in models.Datasets._meta.fields \
                      if f.__class__== FileField]
    #remove some fields we don't want to display on the page
    _removeList = ["user", "paper", "date_created", "status", "comments",
                   #the following are buggy so we're not displaying them 
                   "rep_treat_bw", "rep_treat_peaks", "rep_treat_summits",
                   "rep_cont_bw", 
                   ]
    for r in _removeList: fields.remove(r);


    datasets = models.Datasets.objects.all().order_by("id")
    paginator = Paginator(datasets, _items_per_page) #25 dataset per page
    try:
        page = int(request.GET.get('page', '1'))
        #if givent an id, then go to the page that contains that id
        dset_id = int(request.GET.get('id', '-1'))

        if dset_id != -1:
            #try to find the page that the dset is on
            def binSearchDset(d_id, start, end):
                """binary search datasets to find d_id obj, returns
                the index if found, otherwise none
                """
                if start > end:
                    return None

                mid = (start + end) / 2
                if datasets[mid].id == d_id:
                    return mid
                else:
                    if (datasets[mid].id > d_id):
                        return binSearchDset(d_id, start, mid -1)
                    else:
                        return binSearchDset(d_id, mid+1, end)

            i = binSearchDset(dset_id, 0, len(datasets))
            if i:
                #if we found it
                page = (i / _items_per_page) + 1
            else:
                page = 1
        elif page == -1:
            #special case -1 = last page
            #pg = paginator.page(paginator.num_pages);
            page = paginator.num_pages
    except ValueError:
        page = 1
    try:
        pg = paginator.page(page)
    except (EmptyPage, InvalidPage):
        pg = paginator.page(paginator.num_pages)

    return render_to_response('datacollection/datasets.html', locals(),
                              context_instance=RequestContext(request))

@admin_only
def samples(request):
    """Routing based on the status--which is through a cookie
    NOTE: saving the status is done in js-land!
    """
    #get the js cookie object: samplesPage, convert to python object
    tmp = None
    
    if "samplesPage" in request.COOKIES and request.COOKIES['samplesPage']:
        #unquote b/c the object is stored as HTTP string 
        tmp = json.loads(unquote(request.COOKIES['samplesPage']))

    if tmp and "status" in tmp and tmp["status"]:
        status = tmp["status"]
    else:
        status = "imported"

    #print status

    if status == "all":
        samples = models.Samples.objects.all()
    else:
        samples = models.Samples.objects.filter(status=status)

    return samples_meta(request, samples, status) 
                        #"datacollection/samples_%s.html" % status)

    #route based on status
    #return getattr(_this_mod, "samples_%s" % status)(request)

    #return render_to_response('datacollection/foo.html', locals(),
    #                          context_instance=RequestContext(request))


#NOTE: i sould cache these!!
@admin_only
def samples_meta(request, samples, status):
    """View all of the samples in an excel like table
    IF given species, factor_type, and/or paper url params, then we further
    filter the results accordingly;
    [other fields: factor, antibody, platform, cell type, tissue type,
    cell type, cell pop, strain, condition]
    IF url param uploader is sent, we use uploader instead of user
    """
    statuses = ['imported', 'new', 'all', 'ignored']
    _numbersOnly = re.compile("^\d+$")
    _textAndNums = re.compile("^[\w|\-|\.|\d| ]+$")
    _null = re.compile("^\s*$")
    boxesPerLine=7

    #unzip _adminSidebar
    adminSidebar, adminSidebarNames = zip(*_adminSidebar)
    sidebarURLs = [reverse(p) for p in adminSidebar]
    sidebar = zip(adminSidebar, sidebarURLs, adminSidebarNames)
    currpage = "samples"

    fieldsAbbrev = [('id', 'i'), ('unique_id', 'i'), 
                    ('name', ''), ('factor', 'f'),
                    ('antibody', 'a'), ('cell_line', 'cl'), 
                    ('cell_type', 'ct'), ('cell_pop', 'cp'), 
                    ('tissue_type', 'tt'), ('disease_state', 'ds'),
                    ('strain', 'sn'), ('species', 's'), ('assembly', 'as'),
                    ('fastq_file', 'ff'), ('bam_file', 'bf'),
                    #('TREATS', 't'), ('CONTS', 'c'), 
                    ('dataset', 'd'), ('paper','p'),
                    ('condition', ''), ('description', ''),
                    ('status', '')]
    #fields = ['id', 'unique_id', 'fastq_file', 'bam_file']
    fields, abbrev = zip(*fieldsAbbrev)
    fields = list(fields)
    abbrev = list(abbrev)

    #idFields = ["TREATS", "CONTS", "paper"]
    fileFields = [f.name for f in models.Datasets._meta.fields \
                      if f.__class__== FileField]

    #samples = models.Samples.objects.all()

    #note: we have to keep track of these URL params so that we can feed them
    #into the paginator, e.g. if we click on platform=1, then when we paginate
    #we want the platform param to be carried through
    rest = ""

    #this is the tring the user inputted in the search box, we preserve that
    if "search" in request.GET:
        search = request.GET['search']
        rest = "&search=%s" % search

    #ESOTERIC NOTE: The way we are doing this is backwards, we are checking 
    #or certain search fields:vals in the query, instead we should be going 
    #through the query and trying to understand each term.  BUT again, this
    #is an esoteric note!
    searchFlds = ['factor', 'antibody', 'cell_type', 'cell_line', 'cell_pop',
                  'tissue_type', 'disease_state', 'strain', 'assembly', 
                  #others!
                  ]
    for f in searchFlds:
        if f in request.GET:
            val = request.GET[f]
            rest += "&%s=%s" % (f, val)
            if _numbersOnly.match(val):
                params = {"%s__id" % f:val}
                samples = samples.filter(**params)
            elif _textAndNums.match(val):
                params = {"%s__name__icontains" % f:val}
                samples = samples.filter(**params)
            elif _null.match(val):
                params = {"%s__isnull" % f:True}
                samples = samples.filter(**params)
            else:
                #BAD apple ruins the search (bunch)
                samples = []

    #special searches
    if 'id' in request.GET:
        if _numbersOnly.match(request.GET['id']):
            #ID
            samples = [samples.get(id=request.GET['id'])]
        elif _textAndNums.match(request.GET['id']):
            #UNIQUE ID
            samples = samples.filter(unique_id__iexact=request.GET['id'])
        else:
            #WHERE UNIQUE ID is null
            samples = samples.filter(unique_id__isnull=True)
        rest += "&id=%s" % request.GET['id']

    if 'paper' in request.GET:
        val = request.GET['paper']
        if _numbersOnly.match(val):
            #IS it a pmid or a index?--PMIDs > 10000000 (first: 17512414)
            val = int(val)
            if val < 10000000: #ID
                samples = samples.filter(paper__id=val)
            else:
                samples = samples.filter(paper__pmid=val)
        elif _null.match(val):
            samples = samples.filter(paper__isnull=True)
        rest += "&%s=%s" % ('paper', val)

    if 'dataset' in request.GET:
        val = request.GET['dataset']
        if _numbersOnly.match(val):
            d = models.Datasets.objects.get(pk=int(val))
            #DROP THIS!!! see below!
            #samples = [s for s in d.treats.all()]
            #samples.extend(d.conts.all())
            ###NOTE: this is a really cool way to concatenate QuerySets:
            #ref: https://groups.google.com/forum/?hl=en&fromgroups=#!topic/django-users/0i6KjzeM8OI
            samples = d.treats.all() | d.conts.all()
        elif _null.match(val):
            #samples = models.Samples.objects.filter(Q(myTreatments__isnull=True), Q(myControls__isnull=True))
            samples = samples.filter(TREATS__isnull=True, CONTS__isnull=True)
        rest += "&%s=%s" % ('dataset', val)

    if 'fastq_file' in request.GET:
        val = request.GET['fastq_file']
        if _null.match(val):
            samples = samples.filter(fastq_file__isnull=True)|samples.filter(fastq_file__exact='')
        rest += "&%s=%s" % ('fastq_file', val)

    if 'bam_file' in request.GET:
        val = request.GET['bam_file']
        if _null.match(val):
            samples = samples.filter(bam_file__isnull=True)|samples.filter(bam_file__exact='')
        rest += "&%s=%s" % ('fastq_file', val)


    if 'species' in request.GET:
        val = request.GET['species']
        if _numbersOnly.match(val): 
            #Species id, 1-hs, 2=mm
            samples = samples.filter(species__id=val)
        elif _textAndNums.match(val): 
            #text, e.g. hs--note we ignore 'Homo sapiens'
            _sMap = {'HS':1, 'MM':2}
            val = _sMap[val.upper()] if val.upper() in _sMap else ""
            samples = samples.filter(species__id=val)
        elif _null.match(val):
            samples = samples.filter(species__isnull=True)
        else:
            samples = []
        rest += "&species=%s" % request.GET['species']
        
    # if 'ftype' in request.GET:
    #     samples = samples.filter(factor__type=request.GET['ftype'])
    #     rest += "&ftype=%s" % request.GET['ftype']

    # if 'platform' in request.GET:
    #     samples = samples.filter(platform=request.GET['platform'])
    #     rest += "&platform=%s" % request.GET['platform']
        
    #DROP!!!!
    # if 'condition' in request.GET:
    #     samples = samples.filter(condition=request.GET['condition'])
    #     rest += "&condition=%s" % request.GET['condition']

    # if 'lab' in request.GET:
    #     samples = [s for s in samples \
    #                 if smart_str(s.paper.lab) == smart_str(request.GET['lab'])]
    #     rest += "&lab=%s" % request.GET['lab']
    
    #here is where we order things by ID
    #NOTE: sometimes samples is just a list, so we have to check
    if hasattr(samples, "order_by"):
        samples = samples.order_by("id")

    #control things w/ paginator
    #ref: http://docs.djangoproject.com/en/1.1/topics/pagination/
    paginator = Paginator(samples, _items_per_page) #25 dataset per page
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        pg = paginator.page(page)
    except (EmptyPage, InvalidPage):
        pg = paginator.page(paginator.num_pages)

    #print 'datacollection/samples_%s.html' % status
    return render_to_response('datacollection/samples_%s.html' % status, 
                              locals(),
                              context_instance=RequestContext(request))
    #return render_to_response(template, locals(),
    #                          context_instance=RequestContext(request))

#END: The main views

def change_samples_status(request):
    """Given http params, samples (list of ids) and status (a string),
    we set the status of the samples and reload the page"""
    if 'samples' in request.GET and 'status' in request.GET:
        tmp = [models.Samples.objects.get(pk=i) \
                   for i in request.GET['samples'].split(',')]
        status = request.GET['status'].strip()
        #print request.GET['redirect']
        for s in tmp:
            s.status = status
            s.save()
    return HttpResponseRedirect(reverse('samples')+request.GET['redirect'])

#------------------------------------------------------------------------------

def get_datasets(request, paper_id):
    """return all of the datasets associated w/ paper_id in json
    Fields: gsmid, *platform, (platform)experiment_type, *species,
    factor, *cell_type, file
    * means that if it is set to 0, then inherit the paper's information
    """
    paper = models.Papers.objects.get(id=paper_id)
    datasets = models.Datasets.objects.filter(paper=paper_id)
    
    dlist = ",".join([jsrecord.views.jsonify(d) for d in datasets])
    return HttpResponse("[%s]" % dlist)


#DROP the FOLLOWING fn/view?
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/")
    else:
        form = UserCreationForm()
    return render_to_response("registration/register.html", locals(),
                              context_instance=RequestContext(request))


def paper_submission(request):
    sidebarURLs = [reverse(p) for p in _sidebarPages]
    sidebar = zip(_sidebarPages, sidebarURLs, _sidebarNames)
    currpage = "paper_submission"

    #val_dict = {'pmid': 0} #, 'title': 0, 'authors': 0}
    title = "Paper Submission Form"
    if request.method == 'POST':
        tmp = models.PaperSubmissions()
        tmp.pmid = request.POST['pmid']
        tmp.gseid = request.POST['gseid']
        tmp.submitter_name = request.POST['submitter_name']
        tmp.ip_addr = request.META.get('REMOTE_ADDR')

        #check for uniqueness
        if tmp.pmid:
            paper_dup = models.Papers.objects.filter(pmid=tmp.pmid)
            submit_dup = models.PaperSubmissions.objects.filter(pmid=tmp.pmid)
        elif tmp.gseid:
            paper_dup = models.Papers.objects.filter(gseid__iexact=tmp.gseid)
            submit_dup = models.PaperSubmissions.objects.filter(gseid__iexact=tmp.gseid)
        else:
            msg = "Please enter the Pubmed ID or the GSEID of the paper."
            return render_to_response('datacollection/paper_submission.html',
                                      locals(),
                                      context_instance=RequestContext(request))

        if paper_dup or submit_dup:
            msg = "This paper is already submitted or in the collection. \
            Thank you."
        else:
            msg = "Submission successful Thank you."
            #set to default status
            tmp.status = models.DEFAULT_SUBMISSION_STATUS
            
            try:
                tmp.pmid = int(tmp.pmid)
            except:
                tmp.pmid = 0

            if tmp.pmid > FIRST_PMID:
                #print "%s\t%s" % (tmp.pmid, FIRST_PMID)
                tmp.save()
            elif tmp.gseid != '':
                tmp.save()
            #else: IGNORED
            
    return render_to_response('datacollection/paper_submission.html',
                              locals(),
                              context_instance=RequestContext(request))

@admin_only
def submissions_admin(request):
    """View of paper submissions where curators can change the status"""
    title = "Submission Admin page"
    statuses = [first for (first, sec) in models.SUBMISSION_STATUS]
    if 'status' in request.GET and request.GET['status'] in statuses:
        #filter by the status passed in
        status = request.GET['status']
        submissions = models.PaperSubmissions.objects.filter(status=status)
    else:
        #default to all
        submissions = models.PaperSubmissions.objects.all()
    return render_to_response('datacollection/submissions_admin.html',
                              locals(),
                              context_instance=RequestContext(request))

def _import_paper(pmid, user, save=True):
    """Given a gseid, tries to import all of the information associated
    with that geo entry and create a Paper model object
    this is a helper fn to the auto_paper_import;
    returns the paper model object"""
    pmedQuery = entrez.PaperAdapter(pmid)
    attrs = ['pmid', 'gseid', 'title', 'abstract', 'pub_date']

    #try to create a new paper
    tmp = models.Papers()
    for a in attrs:
        #tmp.a = pmedQuery.a
        setattr(tmp, a, getattr(pmedQuery, a))
        
    #deal with authors
    tmp.authors = ",".join(pmedQuery.authors)

    #set the journal
    JM = models.Journals
    (journal,created) = JM.objects.get_or_create(name=pmedQuery.journal)
    tmp.journal = journal
            
    #add automatic info
    tmp.user = user
    tmp.date_collected = datetime.datetime.now()
    
    if save:
        tmp.save()

    return tmp
    

@admin_only
def auto_paper_import(request):
    """View of auto_paper importer where curators can try to fetch GEO
    information using pubmed ids"""
    if request.method == "POST":
        #the user is trying to autoimport a paper
        if request.POST['pmid']:
             tmp = _import_paper(request.POST['pmid'], request.user)
    else:
        pass

    return render_to_response('datacollection/auto_paper_import.html',
                              locals(),
                              context_instance=RequestContext(request))
@admin_only
def gsm_parser_demo(request):
    """View of auto_paper importer where curators can try to fetch GEO
    information using pubmed ids"""
    if request.method == "POST":
        #the user is trying to autoimport a paper
        if request.POST['pmid']:
            tmp = _import_paper(request.POST['pmid'], request.user)
    else:
        pass

    return render_to_response('datacollection/gsm_parser_demo.html',
        locals(),
        context_instance=RequestContext(request))


@admin_only
def paper_profile(request, paper_id):
    """View of the paper_profile page"""
    paper = models.Papers.objects.get(id=paper_id)
    datasets = models.Datasets.objects.filter(paper=paper_id)
    samples = models.Samples.objects.filter(paper=paper_id)
    return render_to_response('datacollection/paper_profile.html',
                              locals(),
                              context_instance=RequestContext(request))
                
@admin_only
def admin(request):
    """Admin page"""
    papers = models.Papers.objects.all()
    return render_to_response('datacollection/admin.html', locals(),
                              context_instance=RequestContext(request))

@admin_only
def dataset_profile(request, dataset_id):
    """View of the paper_profile page"""
    dataset = models.Datasets.objects.get(id=dataset_id)
    try:
        summary = models.DatasetDhsStats.objects.get(dataset=dataset)
    except:
        pass
    
    return render_to_response('datacollection/dataset_profile.html',
                              locals(),
                              context_instance=RequestContext(request))

@admin_only
def sample_profile(request, sample_id):
    """View of the paper_profile page"""
    sample = models.Samples.objects.get(id=sample_id)
    #treatments = sample.treatments.split(",")
    #datasets = [models.Datasets.objects.get(id=d) for d in dsets]
    return render_to_response('datacollection/sample_profile.html',
                              locals(),
                              context_instance=RequestContext(request))


def _allSameOrNone(objs, attr):
    """If the all of the objects.attr are the same, return that attr,
    else return None
    """
    if len(objs) > 0:
        tmp = getattr(objs[0], attr)
        for o in objs:
            if tmp != getattr(o, attr):
                return None
        return tmp
    else:
        return None
    
@admin_only
def batch_update_datasets(request):
    """A page that allows the user to make batch updates to a set of datasets.
    the datasets are specified in the 'dataset' url
    """
    title = "Batch Update Datasets"
    fields = forms.BatchUpdateDatasetsForm.Meta.fields
    if request.method == "POST":
        dsets = [models.Datasets.objects.get(pk=id) \
                 for id in request.GET['datasets'].split(',')]
        for d in dsets:
            form = forms.BatchUpdateDatasetsForm(request.POST, instance=d)
            if form.is_valid():
                tmp = form.save()
        return HttpResponseRedirect(request.POST['next'])
    else:
        if 'next' in request.GET:
            next = request.GET['next']
        if 'datasets' in request.GET:
            datasets = request.GET['datasets']
            dsets = [models.Datasets.objects.get(pk=id) \
                     for id in datasets.split(',')]
            tmp = models.Datasets()
            for f in fields:
                setattr(tmp, f, _allSameOrNone(dsets, f))
            form = forms.BatchUpdateDatasetsForm(instance=tmp)
    return render_to_response('datacollection/batch_update_datasets_form.html',
                              locals(),
                              context_instance=RequestContext(request))
#OBSOLETE
# def search(request):
#     """the search page"""
#     return render_to_response('datacollection/search.html',
#                               locals(),
#                               context_instance=RequestContext(request))

def delete_view_factory(name, model, redirect='home'):
    """Generates generic delete views
    """
    def generic_delete_view(request):
        """this fn was auto_generated in delete_view_factory
        name = papers, datasets, samples
        """
        if name in request.GET:
            tmp = [model.objects.get(pk=id) \
                   for id in request.GET[name].split(',')]
            for o in tmp:
                o.delete()
        return HttpResponseRedirect(reverse(redirect))
    return admin_only(generic_delete_view)

delete_datasets = delete_view_factory('datasets', models.Datasets, 'datasets')
delete_papers = delete_view_factory('papers', models.Papers, 'papers')
delete_samples = delete_view_factory('samples', models.Samples, 'samples')

@admin_only
def generic_delete(request, model_name):
    """Not to be confused with the inner-fn of delete_view_factory, this 
    view supports the model pages, e.g. platforms, factors delete btn
    """
    model = getattr(models, model_name)

    next = model_name.lower()
    if 'next' in request.GET:
        next = request.GET['next']

    if 'objects' in request.GET:
        tmp = [model.objects.get(pk=i) \
                   for i in request.GET['objects'].split(',')]
        for o in tmp:
            o.delete()
    return HttpResponseRedirect(next)

@admin_only
def generic_merge(request, model_name):
    """This function helps support the fieldsView mergeBtn:
    It takes a set of meta-field objects, e.g. Factors and associated the 
    samples with the object (i.e. factor) that has the highest id, and 
    deletes the others.
    """
    _map = {'Factors':'factor', 'Antibodies':'antibody', 
            'CellLines':'cell_line', 'CellTypes':'cell_type', 
            'CellPops':'cell_pop', 'TissueTypes':'tissue_type',
            'DiseaseStates':'disease_state', 'Strains':'strain', 
            'Species':'species'}
    model = getattr(models, model_name)

    next = 'fieldsView'
    if 'next' in request.GET:
        next = request.GET['next']

    if 'objects' in request.GET:
        tmp = [model.objects.get(pk=i) \
                   for i in request.GET['objects'].split(',')]
        if tmp:
            first = tmp[0]
            
            #re-route all samples to be associated with first
            for o in tmp[1:]:
                for s in o.samples_set.all():
                    #set them
                    setattr(s, _map[model_name], first)
                    s.save()
                o.delete()
    return HttpResponseRedirect(next)

#cache it for a hour
#@cache_page(60 * 60 * 1)
def stats(request):
    """Our stats engine--queries the db and returns info that the users might
    want.
    There are two supported types: sum and time.
    An example of a sum count is when you want to know the number of
    datasets by disease state:
    URL: count?type=sum&model=Datasets&field=disease_state
    Ret: [{label:'AML', count:22}, {label:'normal', count:594}...]
    NOTE: there is no guarantee on the ordering

    A time count is when you are interested in the growth of something over
    time, e.g. how many HK4ME datasets are there over time?
    URL: count?type=time&model=Datasets&field=factor&value=HK4ME3
    Ret: [{year:2005, by_month:[1,2,3,4,5,6,7,8,9,10,11,12], total:78},
          {year:2006, ...}]

    With this info, the client should be able to generate an appropriate graph
    """
    _timeout = 60*60 #1 hour
    if 'type' in request.GET and request.GET['type'] == 'sum':
        #try the cache
        key = "%s_%s_%s" % (request.GET['type'], request.GET['model'],
                            request.GET['field'])
        if cache.get(key):
            return HttpResponse(json.dumps(cache.get(key)))
        
        model = getattr(models, request.GET['model'])
        field = request.GET['field']
        tmp = model.objects.values("%s__name" % field).annotate(count=Count(field)).order_by('-count')
        #want to assign the field__name to label
        #NOTE: this won't work
        #tmp2 = [setattr(x, 'label', getattr(x,'%s__name'%field)) for x in tmp]
        tmp2 = []
        for x in tmp:
            x['label'] = x["%s__name" % field]
            tmp2.append(x)

        #save to cache
        cache.set(key, tmp2, _timeout)
        
        return HttpResponse(json.dumps(cache.get(key)))
    elif 'type' in request.GET and request.GET['type'] == 'ssum':
        #really just used for Papers by labs
        #special sum type--like sum but for doesn't rely on django--can be slow
        #fields can also reference foreign keys, e.g. model = Dataset,
        #field = paper__lab --using django __ as separator

        #try the cache
        key = "%s_%s_%s" % (request.GET['type'], request.GET['model'],
                            request.GET['field'])
        if cache.get(key):
            return HttpResponse(json.dumps(cache.get(key)))

        model = getattr(models, request.GET['model'])
        field = request.GET['field'].split("__")
        tmp = model.objects.all()
        #build up a dictionary
        count = {}
        for x in tmp:
            val = x
            for f in field:
                if val:
                    val = getattr(val, f)
            if val:
                #if it's not a string
                if type(val) != type(''):
                    val = val.__str__()
                if val in count:
                    count[val] = count[val] + 1
                else:
                    count[val] = 1
        ret = [{'label':f, 'count':count[f]} for f in count]
        tmp2 = sorted(ret, key=lambda x: x['count'], reverse=True)
        
        #save to cache
        cache.set(key, tmp2, _timeout)
        
        return HttpResponse(json.dumps(cache.get(key)))
    elif 'type' in request.GET and request.GET['type'] == 'time':
        return HttpResponse(json.dumps([]))
    else:
        return HttpResponse(json.dumps([]))
#         #NOTE: this always references the paper.pub_date--for date_collected,
#         #i.e. stats about our db, we'll have to make another stat type
        
#         #Get the date ranges for our datasets
#         start = _dateRange['pub_date__min']
#         end = _dateRange['pub_date__max']
#         #print start.year
#         #print end.year
#         model = getattr(models, request.GET['model'])
#         field = request.GET['field']
#         val = request.GET['value']

#         ret = []
#         for y in range(start.year, end.year + 1):
#             tmp = {'year':y}
#             by_month = []
#             for m in range(1, 13):
#                 q = model.objects.filter(disease_state=1)#"%s=%s" % (field,val))
#                 if request.GET['model'] == 'Datasets':
#                     prefix = "paper__"
#                 else:
#                     prefix = ""
                    
#                 q.filter("%spub_date__year=%s" % (prefix, y),
#                          "%spub_date__month=%s" % (prefix, m))
                
                             
#                 #.filter(paper__pub_date__year=y, paper__pub_date__month=m).aggregate(count=Count(field))
#                 #by_month.append(c['count'])
#             #tmp['by_month'] = by_month
#             #tmp['total'] = sum(by_month)
#             ret.append(tmp)
#         print ret
#         return HttpResponse(json.dumps(ret))


def dcstats(request):
    """the stats page"""
    sidebarURLs = [reverse(p) for p in _sidebarPages]
    sidebar = zip(_sidebarPages, sidebarURLs, _sidebarNames)
    currpage = "dcstats"
    return render_to_response('datacollection/dcstats.html',
                              locals(),
                              context_instance=RequestContext(request))

def help(request):
    """the user's help page"""
    sidebarURLs = [reverse(p) for p in _sidebarPages]
    sidebar = zip(_sidebarPages, sidebarURLs, _sidebarNames)
    currpage = "help"
    return render_to_response('datacollection/help.html',
                              locals(),
                              context_instance=RequestContext(request))

def contact(request):
    """the contact page"""
    sidebarURLs = [reverse(p) for p in _sidebarPages]
    sidebar = zip(_sidebarPages, sidebarURLs, _sidebarNames)
    currpage = "contact"
    return render_to_response('datacollection/contact.html',
                              locals(),
                              context_instance=RequestContext(request))

    
@admin_only
def admin_help(request, page):
    """Help page for administrators, w/ optional page param"""
    if page:
        if page.endswith("/"):
            page = page[:-1]
        return render_to_response('datacollection/admin_help/%s.html' % page,
                                  locals(),
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('datacollection/admin_help/index.html',
                                  locals(),
                                  context_instance=RequestContext(request))

#------------------------------------------------------------------------------
# Action Btns BEGIN
#------------------------------------------------------------------------------
def _check_for_files(sample):
    """Checks to make sure that the raw files associated for each of the 
    sample's dataset is present.
    Returns a list of datasets whose raw files are missing; [] means the 
    sample's files are all there!
    """
    missing_files_list = []

    datasets = [models.Datasets.objects.get(pk=id) \
                    for id in sample.treatments.split(",")]
    
    if sample.controls:
        datasets.extend([models.Datasets.objects.get(pk=id) \
                             for id in sample.controls.split(",")])

    for d in datasets:
        #check db entry
        if not d.raw_file:
            missing_files_list.append(int(d.id))
        #check file existence
        elif not os.path.exists(d.raw_file.path):
            missing_files_list.append(d.raw_file.path)
    
    return missing_files_list
    

@admin_only
def check_raw_files(request, sample_id):
    """If the sample's status is 'new', checks to see if that the raw files
    are uploaded/loaded for all of the datasets assoc. w/ the sample
    IF this condition holds, changes the status to 'checked', 
    OTHERWISE the status is 'error' and a msg is appended to comments
    """
    sample = models.Samples.objects.get(pk=sample_id)
    page = 1
    if "page" in request.GET:
        page = request.GET['page']

    if sample.status == "new":
        missing_files_list = _check_for_files(sample)

        if missing_files_list: #some missing files-->ERROR
            sample.status = "error"
            sample.comments = "Datasets %s are missing files" % \
                missing_files_list
            sample.save()
        else:
            #No err!
            sample.status = "checked"
            sample.save()

    #redirect to the samples view
    return HttpResponseRedirect(reverse('samples')+("?page=%s" % page))

@admin_only
def run_analysis(request, sample_id):
    """
    Tries to: 
    0. runs to make sure that all datasets have their files
       (redundant w/ check raw files)
    1. calls pipeline runner script on the sample
    
    BLAH! more here! but later!
    """
    sample = models.Samples.objects.get(pk=sample_id)
    page = 1
    if "page" in request.GET:
        page = request.GET['page']

    missing_files_list = _check_for_files(sample)
    if missing_files_list:
        sample.status = "error"
        sample.comments = "Datasets %s are missing files" % \
            missing_files_list
        sample.save()
        return HttpResponseRedirect(reverse('samples')+("?page=%s" % page))
    else: # ok to proceed!
        cwd = os.getcwd()
        working_dir = os.path.join(settings.MEDIA_ROOT, "data", "tmp", 
                                   "sample%s" % sample.id)
        #if not os.path.exists(working_dir):
            #os.mkdir(working_dir)
            #os.chdir(working_dir)
        conf_f = ConfGenerator.generate(sample, request.user,working_dir,False)
        run_sh = RunSHGenerator.generate(sample, conf_f, request.user,
                                         working_dir)

        # run the script as a daemon
        proc = subprocess.Popen(["python", "daemonize.py"], cwd=working_dir)
        
        sample.status = "running"
        sample.save()

    #redirect to the samples view
    return HttpResponseRedirect(reverse('samples')+("?page=%s" % page))


@admin_only
def download_file(request, dataset_id):
    """Tries to download the file for the given dataset"""
    dataset = models.Datasets.objects.get(pk=dataset_id)

    page = 1
    if "page" in request.GET:
        page = request.GET['page']

    #do the stuff here!
    #pattern: ftp://(server) (path) (file)
    #NOTE: this pattern may be buggy!
    url_pattern = "^ftp://((\w|-)+\.?)+(/(\w|-)+)*(/((\w|-)+\.)*\w+)$"
    if not re.match(url_pattern, dataset.raw_file_url):
        dataset.status = "error"
        dataset.comments = "The file_url %s is invalid" % dataset.raw_file_url
        dataset.save()
        return HttpResponseRedirect(reverse('datasets')+("?page=%s" % page))
    else: # ok to proceed!
        cwd = os.getcwd()
        working_dir = os.path.join(settings.MEDIA_ROOT, "data", "tmp", 
                                   "dataset%s" % dataset.id)
        dnld_sh = DnldSHGenerator.generate(dataset, request.user, working_dir)
        proc = subprocess.Popen(["python", "daemonize.py"], cwd=working_dir)
        
    dataset.status = "transfer" 
    dataset.save()

    #redirect to the datasets view
    return HttpResponseRedirect(reverse('datasets')+("?page=%s" % page))

def _auto_dataset_import(paper, user, gsmids):
    """Given a paper id and a set of gsmids, this fn tries to create the
    datasets and associate it with the paper
    NOTE: we are also adding a check for the datasets to see if they're 
    already in the system
    """

    for gsmid in gsmids:
        #check if the dataset already exists
        (tmp, created) = models.Datasets.objects.get_or_create(gsmid=gsmid, defaults={"date_collected": datetime.datetime.now(), "user":user, "paper":paper})
        if created:
            geoQuery = entrez.DatasetAdapter(gsmid)
        
            attrs = ['gsmid', 'name', 'raw_file_url']
            for a in attrs:
                setattr(tmp, a, getattr(geoQuery, a))

            (tmp.raw_file_type, ignored) = models.FileTypes.objects.get_or_create(name=geoQuery.raw_file_type)

            platform = entrez.PlatformAdapter(geoQuery.platform)
            (tmp.platform, ignored) = models.Platforms.objects.get_or_create(gplid=platform.gplid, name=platform.name, technology=platform.technology)
            (tmp.species, ignored) = models.Species.objects.get_or_create(name=geoQuery.species)
            tmp.save()

@admin_only
def import_datasets(request, paper_id):
    """Tries to import the datasets associated with the paper.
    NOTE: before we returned JSON, but now we are making it more action-btn 
    like check_raw_files, run_analysis, etc
    """
    paper = models.Papers.objects.get(pk=paper_id)
    geoQuery = entrez.PaperAdapter(paper.pmid)
    _auto_dataset_import(paper, paper.user, geoQuery.datasets)
    
    page = 1
    if "page" in request.GET:
        page = request.GET['page']

    paper.status = "datasets"
    paper.save()

    #redirect to the papers view
    return HttpResponseRedirect(reverse('papers')+("?page=%s" % page))

@admin_only
def download_paper_datasets(request, paper_id):
    """Tries to download the datasets associated with the paper--calls the 
    download_dataset fn
    """
    paper = models.Papers.objects.get(pk=paper_id)
    datasets = models.Datasets.objects.filter(paper=paper_id)

    page = 1
    if "page" in request.GET:
        page = request.GET['page']

    #call download_datasets but ignore the return
    for d in datasets:
        #sending request is ok--b/c request.page doesn't really affect things
        ignored = download_file(request, d.id)

    paper.status = "transfer"
    paper.save()

    #redirect to the papers view
    return HttpResponseRedirect(reverse('papers')+("?page=%s" % page))
#------------------------------------------------------------------------------
# Action Btns END
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Model Pages
#------------------------------------------------------------------------------
#2012-07-19: changing this Factory to take in modelName instead of models b/c
#I need to send in modelNames to the templates, so we can use jsrecord on them
def modelPagesFactory(modelName, base_name):
    def generic_model_view(request):
        #unzip _adminSidebar
        adminSidebar, adminSidebarNames = zip(*_adminSidebar)
        sidebarURLs = [reverse(p) for p in adminSidebar]
        sidebar = zip(adminSidebar, sidebarURLs, adminSidebarNames)
        currpage = base_name+"s"

        modelNm = modelName
        model = getattr(models, modelName)

        #model fields
        fields = [f.name for f in model._meta.fields]
        
        if (base_name != "species" and base_name != "assembly"):
            title = "%ss" % base_name.title()
        else:
            title = base_name.title()

        objs = model.objects.all().order_by("name")
        current_path = request.get_full_path()
        paginator = Paginator(objs, _items_per_page)
        update_form = "update_%s_form" % base_name
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        try:
            pg = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pg = paginator.page(paginator.num_pages)
            
        return render_to_response('datacollection/generic_table.html', 
                                  locals(),
                                  context_instance=RequestContext(request))
    return admin_only(generic_model_view)


#DUPLICATE!!! kind of!
generic_model_list = ["Platforms", "Factors", "CellTypes", "CellLines", 
                      "CellPops", "Strains", "Conditions", "Journals", 
                      "DiseaseStates", "Species", "TissueTypes",
                      ]

for name in generic_model_list:
    """
    url name - e.g. /factors/
    base name - e.g. factor
    """
    url_name = name.lower()
    #this is the exception
    if name != "Species":
        base_name = name.lower()[:-1]
    else:
        base_name = url_name
    setattr(_this_mod, url_name, 
            modelPagesFactory(name, base_name))

assemblies = modelPagesFactory(models.Assemblies, "assembly")

def fieldsView(request):
    """view for fields tab"""
    fieldTypes = ["Factors", "Antibodies", "CellLines", "CellTypes", 
                  "CellPops", "TissueTypes", "DiseaseStates", "Strains", 
                  "Species"]
    rest = ""
    search = None
    if "search" in request.GET:
        search = request.GET['search']
        rest = "&search=%s" % search

    tmp=None
    if "fieldsView" in request.COOKIES and request.COOKIES['fieldsView']:
        #unquote b/c the object is stored as HTTP string 
        tmp = json.loads(unquote(request.COOKIES['fieldsView']))

    if tmp and "fieldType" in tmp and tmp["fieldType"]:
        fieldType = tmp["fieldType"]
    else:
        fieldType = "Factors"

    #unzip _adminSidebar
    adminSidebar, adminSidebarNames = zip(*_adminSidebar)
    sidebarURLs = [reverse(p) for p in adminSidebar]
    sidebar = zip(adminSidebar, sidebarURLs, adminSidebarNames)
    currpage = "fieldsView"

    modelNm = fieldType
    model = getattr(models, modelNm)

    #model fields
    fields = [f.name for f in model._meta.fields]
    
    title = "Fields: %s" % fieldType

    if search:
        objs = model.objects.filter(name__icontains=search)
    else:
        objs = model.objects.all()#.order_by("name")

    current_path = request.get_full_path()
    paginator = Paginator(objs, _items_per_page)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        pg = paginator.page(page)
    except (EmptyPage, InvalidPage):
        pg = paginator.page(paginator.num_pages)
        
    #HACK we want to add the number of associated samples
    fields.append("samples")
    for o in pg.object_list:
        setattr(o, "samples", o.samples_set.count())

    return render_to_response('datacollection/generic_table.html', 
                              locals(),
                              context_instance=RequestContext(request))

#------------------------------------------------------------------------------
# search page
#------------------------------------------------------------------------------
#@cache_page(60 * 60 * 1)
def search_papers(request):
    """This view takes a query param, q, and returns the jsonified records for
    all of the papers associated with that query string
    """
    #use paper ids to check for duplicates
    paper_ids = []
    tmp = []
    _timeout = 60*60*24 #1 day
    _hashTAG = "####SEARCH_PAPERS####"
    if 'q' in request.GET:
        key = request.GET['q']
        if cache.get(_hashTAG + key):
            return HttpResponse(cache.get(_hashTAG + key))

        res = SearchQuerySet().filter(content=key)
        for r in res:
            #NOTE: r.model, r.model_name, r.object
            if r.model is models.Datasets:
                p = r.object.paper
            else:
                p = r.object

            if not p.id in paper_ids:
                paper_ids.append(p.id)
                #tmp.append(jsrecord.views.jsonify(p))
                tmp.append(p)

        #sort tmp by pub_date
        def sorter(p):
            #try to sort by pub_date, otherwise use id
            if p and p.pub_date:
                p.pub_date
            else:
                #return id
                p.id
        #tmp.sort(key=lambda p: p.pub_date, reverse=True)
        tmp.sort(key=sorter, reverse=True)
        tmp2 = [jsrecord.views.jsonify(p) for p in tmp]
        
        ret = "[%s]" % ",".join(tmp2)
        cache.set(_hashTAG + key, ret, _timeout)
    #print paper_ids
    return HttpResponse(ret)

def search_factors(request):
    """This view takes a query param and returns a ordered list of factors
    associated with that search term
    """
    all_factors = [] 
    factor_names = []
    ret = []
    _timeout = 60*60*24 #1 day
    _hashTAG = "####SEARCH_FACTORS####"
    if 'q' in request.GET:
        key = request.GET['q']
        if cache.get(_hashTAG + key):
            #Saving query results b/c this could be used later
            res = cache.get(_hashTAG + key)
        else:
            res = SearchQuerySet().filter(content=key)
            cache.set(_hashTAG + key, res, _timeout)

        for r in res:
            #NOTE: r.model, r.model_name, r.object
            if r.model is models.Datasets:
                if r.object.factor.name not in factor_names:
                    all_factors.append(r.object.factor)
                    factor_names.append(r.object.factor.name)
            else: #it's a paper
                for f in r.object.factors:
                    if f not in factor_names:
                        fact = models.Factors.objects.filter(name=f)[0]
                        all_factors.append(fact)
                        factor_names.append(f)
        #sort by id
        all_factors.sort(key=lambda f: f.name)        
        tmp2 = [jsrecord.views.jsonify(f) for f in all_factors]
        
        ret = "[%s]" % ",".join(tmp2)
    return HttpResponse(str(ret))

def search_cells(request):
    """This view takes a query param and returns a ordered list of cells
    associated with that search term
    Cells set = cell lines, cell pops, cell types, and tissue types
    """
    _flds = [("cell_line", models.CellLines), ("cell_pop", models.CellPops), 
             ("cell_type", models.CellTypes), 
             ("tissue_type", models.TissueTypes)]
    all_cells = [] 
    cell_names = []
    ret = []
    _timeout = 60*60*24 #1 day
    _hashTAG = "####SEARCH_CELLS####"
    if 'q' in request.GET:
        key = request.GET['q']
        if cache.get(_hashTAG + key):
            #Saving query results b/c this could be used later
            res = cache.get(_hashTAG + key)
        else:
            res = SearchQuerySet().filter(content=key)
            cache.set(_hashTAG + key, res, _timeout)

        res = SearchQuerySet().filter(content=key)
        for r in res:
            #NOTE: r.model, r.model_name, r.object
            if r.model is models.Datasets:
                for (f, m) in _flds:
                    val = getattr(r.object, f)
                    if val and val.name not in cell_names:
                        all_cells.append(val)
                        cell_names.append(val.name)
            else: #it's a paper
                for (f, mod) in _flds:
                    f = f+"s" #in paper they're plural
                    val = getattr(r.object, f)
                    for i in val:
                        if i not in cell_names:
                            tmp = mod.objects.filter(name=i)[0]
                            all_cells.append(tmp)
                            cell_names.append(i)
        #sort by id
        all_cells.sort(key=lambda c: c.name)        
        tmp2 = [jsrecord.views.jsonify(c) for c in all_cells]
        
        ret = "[%s]" % ",".join(tmp2)
    return HttpResponse(str(ret))


def front(request, rtype):
    """supports the front page retrieval of, for example, the most recent 
    papers (determined by rtype).
    returns JSON
    """
    _timeout = 60*60*24 #1 hr

    #1. go to cache
    if cache.get(rtype):
        return HttpResponse(cache.get(rtype))

    key = "front:all_papers"
    if cache.get(key):
        all_papers = cache.get(key)
    else:
        all_papers = models.Papers.objects.all().order_by("-pub_date")
        cache.set(key, all_papers, _timeout)

    tmp = []
    if (rtype == "all"):
        #papers = models.Papers.objects.all().order_by("-pub_date")
        papers = all_papers
    elif (rtype == "recent"):
        #get most recent 10--NOTE: just like all, but taking latest 10
        #papers = models.Papers.objects.all().order_by("-pub_date")[:10]
        papers = all_papers[:10]
    else:
        papers = []

    tmp = [jsrecord.views.jsonify(p) for p in papers]
    ret = "[%s]" % ",".join(tmp)
    cache.set(rtype, ret, _timeout)

    return HttpResponse(ret)
#------------------------------------------------------------------------------
def factors_view(request):
    """Takes a query param, factors--a list of factor ids, and returns 
    information to fill out the factors view.  First checks factors in 
    the following order: CellLines, CellPop, and then TissueType

    NOTE: we only cache one thing--and that is the when it's all factors!
    THIS may change!
    """
    _MODELS = [('cell_line', models.CellLines),
               ('cell_pop', models.CellPops),
               ('cell_type', models.CellTypes),
               ('tissue_type', models.TissueTypes),
               ]
    _hashTAG = "####SEARCH_FACTORS####"
    #NOTE: we are not jsonifying papers for efficiency sake!
    #but we need to pull the following fields from it--see how we do this below
    _paperFldsToPull = ["pmid", "authors", "last_auth_email", "unique_id", 
                        "reference"]
    _fileFlds = [f.name for f in models.Datasets._meta.fields \
                     if type(f) == FileField]
    _data_dir = os.path.join(settings.MEDIA_ROOT, "data")

    _timeout = 60*60*24 #1 day
    ret = {}
    mnames = []

    #restrict the return with the following
    restrictSetIds = []
    
    if 'factors' in request.GET:
        factors = [models.Factors.objects.get(pk=int(f)) \
                       for f in request.GET['factors'].split(",")]
        sorted(factors, key=lambda f:f.name)
        fnames = [f.name for f in factors]

        #was this associated with a search term?
        if 'search' in request.GET:
            key = request.GET['search']
            #relying on the fact that search is done BEFORE draw Table!
            res = cache.get(_hashTAG + key)
            if res:
                #track what's added
                for r in res:
                    if r.model is models.Datasets:
                        restrictSetIds.append(r.object.id)
                    else: #it's a paper
                        dsets = models.Datasets.objects.filter(paper=r.object)
                        for d in dsets:
                            if d.id not in restrictSetIds:
                                restrictSetIds.append(d.id)
        
        for f in factors:
            #track samples, to ensure no duplicates within factors.
            allDsets = []
            if f.name not in ret:
                ret[f.name] = {}

            for (dsetFld, model) in _MODELS:
                for m in model.objects.all():
                    #build it up
                    #NOTE: the treats fld is the ManyToMany field
                    params = {'treats__factor':f, "treats__"+dsetFld:m}
                    #NOTE: we have to pass in the param as a **
                    tmp = models.Datasets.objects.filter(**params)
                    if restrictSetIds:
                        tmp = [d for d in tmp if d.id not in allDsets\
                                   and d.id in restrictSetIds]
                    else:
                        tmp = [d for d in tmp if d.id not in allDsets]
                    
                    if tmp:
                        if m.name not in mnames:
                            mnames.append(m.name)
                        for d in tmp:
                            allDsets.append(d.id)
                            #Optimization: not jsonifying the papers
                            for fld in _paperFldsToPull:
                                if d.paper and getattr(d.paper, fld):
                                    setattr(d, fld, getattr(d.paper, fld))
                                else:
                                    setattr(d, fld, None)
                            d._meta._virtualfields.extend(_paperFldsToPull)
                            d.paper = None
                            #ADD the qc fields
                            qc = models.Qc.objects.get(id=d.id)
                            #Init to NA
                            d.qc = ['NA' for i in range(1, 11)]
                            for i in range(1,11):
                                d.qc[i -1] = getattr(qc, "qc%s" % i)
                            d._meta._virtualfields.append('qc')

                            #ADD the sample information
                            d.samples = {}
                            d.samples['treats'] = [{'id':s.id, 'unique_id':s.unique_id, 'fastq_file_url':s.fastq_file_url} for s in d.treats.all() if s]
                            d.samples['conts'] = [{'id':s.id, 'unique_id':s.unique_id, 'fastq_file_url':s.fastq_file_url} for s in d.conts.all() if s]
                            d._meta._virtualfields.append('samples')

                            #CHECK if the files exist and are non-zero
                            for f_fld in _fileFlds:
                                f_path = os.path.join(_data_dir, 
                                                      str(getattr(d, f_fld)))
                                #IF the file DNE OR it is empty
                                if not os.path.exists(f_path) or \
                                        not os.path.getsize(f_path):
                                    setattr(d, f_fld, None)

                        dsets = [jsrecord.views.jsonify(d) for d in tmp]
                        ret[f.name][m.name] = dsets

            resp = "{'factors': %s, 'models': %s, 'dsets': %s}" % (json.dumps(fnames), json.dumps(sorted(mnames, cmp=lambda x,y: cmp(x.lower(), y.lower()))), json.dumps(ret))

        return HttpResponse(resp)

    return HttpResponse('[]')

def cells_view(request):
    """Takes a query param, cells--a list of cell_line/cellpop/celltype or 
    tissuetype ids, and returns 
    information to fill out the factors view.  
    """
    def partition(ds):
        """given a set of samples, returns a 4-tuple, indicating which 
        cell_lines, cellpops, cell_type, and tissue type are represented in
        the samples"""
        
        (cls, cps, cts, tts) = ([],[],[],[])
        ls = [(cls, "cell_line"), (cps, "cell_pop"), (cts, "cell_type"),
              (tts, "tissue_type")]
        for d in ds:
            #MUST use the first treatment Sample to get this info
            s = d.treats.all()
            for (lst, fld) in ls:
                val = getattr(s[0], fld)
                if val and val not in lst:
                    lst.append(val)
        return (cls, cps, cts, tts)

    _Mapping = {'cl': "cell_line", 'cp': "cell_pop", 
               'ct': "cell_type", 'tt': "tissue_type"}

    #NOTE: we are not jsonifying papers for efficiency sake!
    #but we need to pull the following fields from it--see how we do this below
    _paperFldsToPull = ["pmid", "authors", "last_auth_email", #"gseid", 
                        "reference"]
    _fileFlds = [f.name for f in models.Datasets._meta.fields \
                     if type(f) == FileField]
    _data_dir = os.path.join(settings.MEDIA_ROOT, "data")

    _hashTAG = "####SEARCH_CELLS####"
    ret = {}
    mnames = []
    fnames = []

    #restrict the return with the following
    restrictSetIds = []

    if 'cells' in request.GET:
        #was this associated with a search term?
        if 'search' in request.GET:
            key = request.GET['search']
            #relying on the fact that search is done BEFORE draw Table!
            res = cache.get(_hashTAG + key)
            if res:
                #track what's added
                for r in res:
                    if r.model is models.Datasets:
                        restrictSetIds.append(r.object.id)
                    else: #it's a paper
                        dsets = models.Datasets.objects.filter(paper=r.object)
                        for d in dsets:
                            if d.id not in restrictSetIds:
                                restrictSetIds.append(d.id)

        #NOTE: the user can only select 1 cell--we use that to our advantage!
        (m, cid) = request.GET['cells'].split(",")
        params = {"treats__"+_Mapping[m]:cid}
        dsets = models.Datasets.objects.filter(**params)
        (cls, cps, cts, tts) = partition(dsets)
        
        if not restrictSetIds:
            #if not using a restriction set, then all of the dset ids is ok!
            restrictSetIds = [d.id for d in dsets]
 
        #assign the datasets to each partition, starting with cls, until we 
        #exhaust the list
        allDsets = [] #this is to track that we're not adding duplicates
        for (ls, fld) in [(cls, "cell_line"), (cps, "cell_pop"),
                          (cts, "cell_type"), (tts, "tissue_type")]:
            for c in ls:
                params = {"treats__"+fld:c}
                tmp = dsets.filter(**params)
                for d in tmp:
                    if d.id not in allDsets and d.id in restrictSetIds:
                        if d.species:
                            #Optimization: not jsonifying the papers
                            for f in _paperFldsToPull:
                                if d.paper and getattr(d.paper, f):
                                    setattr(d, f, getattr(d.paper, f))
                                else:
                                    setattr(d, f, None)
                            d._meta._virtualfields.extend(_paperFldsToPull)
                            d.paper = None

                            #ADD the qc fields
                            qc = models.Qc.objects.get(id=d.id)
                            #Init to NA
                            d.qc = ['NA' for i in range(1, 11)]
                            for i in range(1,11):
                                d.qc[i -1] = getattr(qc, "qc%s" % i)
                            d._meta._virtualfields.append('qc')

                            #ADD the sample information
                            d.samples = {}
                            d.samples['treats'] = [{'id':s.id, 'unique_id':s.unique_id, 'fastq_file_url':s.fastq_file_url} for s in d.treats.all() if s]
                            d.samples['conts'] = [{'id':s.id, 'unique_id':s.unique_id, 'fastq_file_url':s.fastq_file_url} for s in d.conts.all() if s]
                            d._meta._virtualfields.append('samples')

                            #CHECK if the files exist and are non-zero
                            for f_fld in _fileFlds:
                                f_path = os.path.join(_data_dir, 
                                                      str(getattr(d, f_fld)))
                                #IF the file DNE OR it is empty
                                if not os.path.exists(f_path) or \
                                        not os.path.getsize(f_path):
                                    setattr(d, f_fld, None)


                            allDsets.append(d.id)
                            if d.factor not in fnames:
                                fnames.append(d.factor)
                            val = getattr(d, fld)
                            #key to organize the data: cell*_name + species
                            #before it was orgKey=val.name
                            specKey = "h" if d.species == "Homo sapiens" else "m"
                            orgKey = "%s(%s)" % (val, specKey)
                            if orgKey not in mnames:
                                mnames.append(orgKey)
                            
                            if d.factor not in ret:
                                ret[d.factor] = {}
                        
                            if orgKey not in ret[d.factor]:
                                ret[d.factor][orgKey] = []
                            ret[d.factor][orgKey].append(jsrecord.views.jsonify(d))
                        else: 
                            #SKIPPING BAD dsets! 
                            #add to allDsets w/o adding to ret
                            allDsets.append(d.id)
            #once allDsets == dsets, we can return
            if len(allDsets) == len(dsets):
                break;
        resp = "{'factors': %s, 'models': %s, 'dsets': %s}" % \
            (json.dumps(sorted(fnames)), \
                 json.dumps(sorted(mnames, cmp=lambda x,y: cmp(x.lower(), y.lower()))), \
                 json.dumps(ret))
        return HttpResponse(resp)
    return HttpResponse("[]")

@admin_only
def push_meta(request, dataset_id):
    """
    This view pushes the dataset meta information to the tongji server.
    It first creates a temporary file w/ the following info:
    column 1: treatment sample IDs
    column 2: control sample IDs
    column 3: Species of the ChIP sample
    column 4: Factor name of the ChIP sample

    And then it tries to scp the temp file to tongji
    """
    _TEMP_DIR = "/tmp"
    _login_info = "len@compbio2.tongji.edu.cn"
    _dump_path = "/mnt/Storage/DC_meta_temp/"

    d = models.Datasets.objects.get(pk=dataset_id)
    if d:
        fpath = os.path.join(_TEMP_DIR, "%s.txt" % d.id)
        f = open(fpath, "w")
        treats = [str(s.id) for s in d.treats.all()]
        conts = [str(s.id) for s in d.conts.all()]
        f.write("%s\t%s\t%s\t%s\n" % (",".join(treats), ",".join(conts),d.species,d.factor))
        f.close()
        # scp the file
        # note: requires the public key to be an authorized key
        proc = subprocess.Popen(["scp", "%s.txt" % d.id, "%s:%s" % (_login_info, _dump_path)], cwd=_TEMP_DIR)

        return HttpResponse('{\"success\":true}')
    else:
        return HttpResponse('{\"success\":false}')

