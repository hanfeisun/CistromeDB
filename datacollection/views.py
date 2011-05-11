import os
import sys
import datetime
import subprocess
import re

from django.shortcuts import render_to_response, Http404, get_object_or_404
from django.contrib import auth
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect, HttpResponse
#from django.contrib.auth.views import login
from django.core.urlresolvers import reverse
from django.db.models import Q, Count, Max, Min, Avg, query, manager
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core.cache import cache
from django.utils.encoding import smart_str

import models
import forms
import settings
from entrezutils import models as entrez
import jsrecord.views

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

def no_view(request):
    """
    We don't really want anyone going to the static_root.
    However, since we're raising a 404, this allows flatpages middleware to
    step in and serve a page, if there is one defined for the URL.
    """
    raise Http404

def home(request):
    #show the 10 newest papers
    papers = models.Papers.objects.order_by('-date_collected')[:10]
    return render_to_response('datacollection/home.html', locals(),
                              context_instance=RequestContext(request))

@login_required
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

@login_required
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

@login_required
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

@login_required
def new_sample_form(request):
    if request.method == "POST":
        form = forms.SampleForm(request.POST, request.FILES)
        if form.is_valid():
            tmp = form.save(commit=False)
            tmp.user = request.user
            #I'm not sure why the form isn't finding paper OR datasets in
            #request.POST
            tmp.datasets = request.POST['datasets']
            tmp.paper = models.Papers.objects.get(id=request.POST['paper'])
            tmp.save()
            return HttpResponseRedirect(request.POST['next'])
        else:
            print "INVALID Sample FORM"
    else:
        form = forms.SampleForm()
        if 'next' in request.GET:
            next = request.GET['next']
        if 'p' in request.GET:
            paper = request.GET['p']
    return render_to_response('datacollection/new_sample_form.html',
                              locals(),
                              context_instance=RequestContext(request))
#------------------------------------------------------------------------------
#GENERIC FORMS section
def form_view_factory(title_in, form_class):
#    @login_required--see return
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
    return login_required(generic_form_view)

#Cool! but we need the decorators!
generic_forms_list = ['platform','factor','celltype','cellline', 'cellpop',
                      'strain', 'condition', 'journal', 'species', 'filetype',
                      'assembly']
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
    return login_required(generic_update_view)

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

def papers(request, user_id):
    """If given a user_id, shows all of the papers imported by the user,
    otherwise shows all papers in the db"""

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

def weekly_papers(request, user_id):
    """Returns all of the papers that the user worked on since the given date,
    IF date is not given as a param, then assumes date = beginning of the week
    IF NO user_id is given, returns a page allowing the user to select which
    user to view
    """
    if user_id:
        #NOTE: the current url regex doesn't parse out the / from the user_id
        if user_id.endswith("/"):
            user_id = user_id[:-1]
        
        papers = models.Papers.objects.filter(user=user_id)
        today = datetime.date.today()
        begin = today - datetime.timedelta(today.weekday())
        if "date" in request.GET:
            if re.match(_datePattern, request.GET['date']):
                tmp = request.GET['date'].split("-")
                d = datetime.date(int(tmp[0]), int(tmp[1]), int(tmp[2]))
            else:
                d = begin
            papers = papers.filter(date_collected__gte=d)
        else:
            #No date param, take the beginning of the week
            papers = papers.filter(date_collected__gte=begin)

        #is this fragile?
        return render_to_response('datacollection/papers.html', locals(),
                                  context_instance=RequestContext(request))
    else:
        #list users
        title = "Weekly Papers"
        users = auth.models.User.objects.all()
        url = reverse('weekly_papers')
        return render_to_response('datacollection/list_users.html', locals(),
                                  context_instance=RequestContext(request))

#NOTE: i sould cache these!!
def datasets(request, user_id):
    """View all of the datasets in an excel like table; as with papers
    if given a user_id, it will return a page of all of the datsets collected
    by the user
    IF given species, factor_type, and/or paper url params, then we further
    filter the results accordingly;
    [other fields: factor, antibody, platform, cell type, tissue type,
    cell type, cell pop, strain, condition]
    IF url param uploader is sent, we use uploader instead of user
    """
    if user_id:
        if user_id.endswith("/"):
            user_id = user_id[:-1]
        if 'uploader' in request.GET:
            datasets = models.Datasets.objects.filter(uploader=user_id)
        else:
            datasets = models.Datasets.objects.filter(user=user_id)
    else:
        datasets = models.Datasets.objects.all()

    #note: we have to keep track of these URL params so that we can feed them
    #into the paginator, e.g. if we click on platform=1, then when we paginate
    #we want the platform param to be carried through
    rest = ""
    if 'species' in request.GET:
        #dict = {'hs':'Homo sapiens', 'mm':'Mus Musculus'}
        #if request.GET['species'] in dict:
        #    datasets = datasets.filter(species__name=\
        #                               dict[request.GET['species']])
        datasets = datasets.filter(species=request.GET['species'])
        rest += "&species=%s" % request.GET['species']
        
    if 'ftype' in request.GET:
        datasets = datasets.filter(factor__type=request.GET['ftype'])
        rest += "&ftype=%s" % request.GET['ftype']

    if 'paper' in request.GET:
        datasets = datasets.filter(paper=request.GET['paper'])
        rest += "&paper=%s" % request.GET['paper']

    if 'factor' in request.GET:
        factor = models.Factors.objects.get(pk=request.GET['factor'])
        datasets = datasets.filter(factor__name=factor.name)
        rest += "&factor=%s" % request.GET['factor']

    if 'antibody' in request.GET:
        factor = models.Factors.objects.get(pk=request.GET['antibody'])
        datasets = datasets.filter(factor__antibody=factor.antibody)
        rest += "&antibody=%s" % request.GET['antibody']

    if 'platform' in request.GET:
        datasets = datasets.filter(platform=request.GET['platform'])
        rest += "&platform=%s" % request.GET['platform']
        
    if 'celltype' in request.GET:
        celltype = models.CellTypes.objects.get(pk=request.GET['celltype'])
        datasets = datasets.filter(cell_type__name=celltype.name)
        rest += "&celltype=%s" % request.GET['celltype']

    if 'tissuetype' in request.GET:
        celltype = models.CellTypes.objects.get(pk=request.GET['tissuetype'])
        datasets = datasets.filter(cell_type__tissue_type=celltype.tissue_type)
        rest += "&tissuetype=%s" % request.GET['tissuetype']

    if 'cellline' in request.GET:
        datasets = datasets.filter(cell_line=request.GET['cellline'])
        rest += "&cellline=%s" % request.GET['cellline']

    if 'cellpop' in request.GET:
        datasets = datasets.filter(cell_pop=request.GET['cellpop'])
        rest += "&cellpop=%s" % request.GET['cellpop']
                
    if 'strain' in request.GET:
        datasets = datasets.filter(strain=request.GET['strain'])
        rest += "&strain=%s" % request.GET['strain']

    if 'condition' in request.GET:
        datasets = datasets.filter(condition=request.GET['condition'])
        rest += "&condition=%s" % request.GET['condition']

    if 'disease_state' in request.GET:
        datasets = datasets.filter(disease_state=request.GET['disease_state'])
        rest += "&disease_state=%s" % request.GET['disease_state']

    if 'lab' in request.GET:
        datasets = [d for d in datasets \
                    if smart_str(d.paper.lab) == smart_str(request.GET['lab'])]
        rest += "&lab=%s" % request.GET['lab']
        
    #control things w/ paginator
    #ref: http://docs.djangoproject.com/en/1.1/topics/pagination/
    paginator = Paginator(datasets, _items_per_page) #25 dataset per page
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        datasets = paginator.page(page)
    except (EmptyPage, InvalidPage):
        datasets = paginator.page(paginator.num_pages)
        
    return render_to_response('datacollection/datasets.html', locals(),
                              context_instance=RequestContext(request))

def weekly_datasets(request, user_id):
    """Returns all of the datasets that the user worked on since the given date
    IF date is not given as a param, then assumes date = beginning of the week
    IF a url param uploader is given, then we use uploader instead of user to
    get the datasets
    IF NO user_id is given, returns a page allowing the user to select which
    user to view
    """
    if user_id:
        #NOTE: the current url regex doesn't parse out the / from the user_id
        if user_id.endswith("/"):
            user_id = user_id[:-1]
        if 'uploader' in request.GET:
            datasets = models.Datasets.objects.filter(uploader=user_id)
        else:
            datasets = models.Datasets.objects.filter(user=user_id)
        today = datetime.date.today()
        begin = today - datetime.timedelta(today.weekday())
        if "date" in request.GET:
            if re.match(_datePattern, request.GET['date']):
                tmp = request.GET['date'].split("-")
                d = datetime.date(int(tmp[0]), int(tmp[1]), int(tmp[2]))
            else:
                d = begin
            datasets = datasets.filter(date_collected__gte=d)
        else:
            #No date param, take the beginning of the week
            datasets = datasets.filter(date_collected__gte=begin)

        return render_to_response('datacollection/datasets.html', locals(),
                                  context_instance=RequestContext(request))
    else:
        #list users
        title = "Weekly Datasets"
        users = auth.models.User.objects.all()
        url = reverse('weekly_datasets')
        return render_to_response('datacollection/list_users.html', locals(),
                                  context_instance=RequestContext(request))

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

def samples(request):
    """Returns all of the samples
    """
    samples = models.Samples.objects.all()
    paginator = Paginator(samples, _items_per_page) #25 dataset per page
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        pg = paginator.page(page)
    except (EmptyPage, InvalidPage):
        pg = paginator.page(paginator.num_pages)

    return render_to_response('datacollection/samples.html', locals(),
                              context_instance=RequestContext(request))

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

@login_required
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

def _auto_dataset_import(paper, user, gsmids):
    """Given a paper id and a set of gsmids, this fn tries to create the
    datasets and associate it with the paper"""

    for gsmid in gsmids:
        geoQuery = entrez.DatasetAdapter(gsmid)
        tmp = models.Datasets()
        
        attrs = ['gsmid', 'name']#, 'file_url']
        for a in attrs:
            setattr(tmp, a, getattr(geoQuery, a))

        #NOTE: file_url changed to raw_file_url
        tmp.raw_file_url = geoQuery.file_url

        tmp.date_collected = datetime.datetime.now()
        #NOTE: file_type changed to raw_file_type
        (tmp.raw_file_type, created) = models.FileTypes.objects.get_or_create(name=geoQuery.file_type)
        tmp.user = user
        tmp.paper = paper
        
        platform = entrez.PlatformAdapter(geoQuery.platform)
        (tmp.platform, created) = models.Platforms.objects.get_or_create(gplid=platform.gplid, name=platform.name, technology=platform.technology)
        (tmp.species, created) = models.Species.objects.get_or_create(name=geoQuery.species)
        tmp.save()

def _import_paper(gseid, user):
    """Given a gseid, tries to import all of the information associated
    with that geo entry and create a Paper model object
    this is a helper fn to the auto_paper_import;
    returns the paper model object"""
    geoQuery = entrez.PaperAdapter(gseid)
    attrs = ['pmid', 'gseid', 'title', 'abstract', 'pub_date']

    #try to create a new paper
    tmp = models.Papers()
    for a in attrs:
        #tmp.a = geoQuery.a
        setattr(tmp, a, getattr(geoQuery, a))
        
    #deal with authors
    tmp.authors = ",".join(geoQuery.authors)

    #set the journal
    JM = models.Journals
    (journal,created) = JM.objects.get_or_create(name=geoQuery.journal)
    tmp.journal = journal
            
    #add automatic info
    tmp.user = user
    tmp.date_collected = datetime.datetime.now()
    
    tmp.save()
    return tmp
    

@login_required
def auto_paper_import(request):
    """View of auto_paper importer where curators can try to fetch GEO
    information using pubmed ids"""
    if request.method == "POST":
        #the user is trying to autoimport a paper
        if request.POST['gseid']:
            # geoQuery = entrez.PaperAdapter(request.POST['gseid'])
#             attrs = ['pmid', 'gseid', 'title', 'abstract', 'pub_date']

#             #try to create a new paper
#             tmp = models.Papers()
#             for a in attrs:
#                 #tmp.a = geoQuery.a
#                 setattr(tmp, a, getattr(geoQuery, a))
#             #deal with authors
#             tmp.authors = ",".join(geoQuery.authors)

#             #set the journal
#             JM = models.Journals
#             (journal,created) = JM.objects.get_or_create(name=geoQuery.journal)
#             tmp.journal = journal
            
#             #add automatic info
#             tmp.user = request.user
#             tmp.date_collected = datetime.datetime.now()

#             tmp.save()
             tmp = _import_paper(request.POST['gseid'], request.user)
             
#            _auto_dataset_import(tmp.id, request.user, geoQuery.datasets)
# TURN THIS ON IF you want it to work with the paper importer 
#             try: 
#                 tmp.save()

#                 #try to auto import the associated datasets
#                 _auto_dataset_import(tmp.id, request.user, geoQuery.datasets)
                
#                 #json - a flag that is sent in
#                 if 'json' in request.POST and request.POST['json']:
#                     return HttpResponse("{'success':true}")
#             except:
#                 #probably a duplicate entry--silently ignored
#                 sys.stderr.write("autopaperimport error: %s\n\t%s\n" % \
#                                 (sys.exc_info()[0],"probably duplicate entry"))
#                 if 'json' in request.POST and request.POST['json']:
#                     return HttpResponse("{'success':false}")
    else:
        pass

    return render_to_response('datacollection/auto_paper_import.html',
                              locals(),
                              context_instance=RequestContext(request))

def paper_profile(request, paper_id):
    """View of the paper_profile page"""
    paper = models.Papers.objects.get(id=paper_id)
    datasets = models.Datasets.objects.filter(paper=paper_id)
    samples = models.Samples.objects.filter(paper=paper_id)
    return render_to_response('datacollection/paper_profile.html',
                              locals(),
                              context_instance=RequestContext(request))
                
@login_required
def admin(request):
    """Admin page"""
    papers = models.Papers.objects.all()
    return render_to_response('datacollection/admin.html', locals(),
                              context_instance=RequestContext(request))

@login_required
def import_datasets(request, paper_id):
    """Tries to import the datasets associated with the paper"""
    paper = models.Papers.objects.get(pk=paper_id)
    geoQuery = entrez.PaperAdapter(paper.gseid)
    _auto_dataset_import(paper, paper.user, geoQuery.datasets)
        
    return HttpResponse("{success:true}")

@login_required
def download_datasets(request, paper_id):
    """Tries to download the datasets associated with the paper"""
    #NOTE: this uses pip, which is in DEPLOY_DIR/importer
    path = os.path.join(settings.DEPLOY_DIR, "importer", "pip.py")
    pid = subprocess.Popen([path, paper_id]).pid
    return HttpResponse("{success:true}")

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

def sample_profile(request, sample_id):
    """View of the paper_profile page"""
    sample = models.Samples.objects.get(id=sample_id)
    dsets = sample.datasets.split(",")
    datasets = [models.Datasets.objects.get(id=d) for d in dsets]
    return render_to_response('datacollection/sample_profile.html',
                              locals(),
                              context_instance=RequestContext(request))

@login_required
def report(request):
    """Generates the weekly report page
    Takes an optional url param date that tells us which date to generate the
    report from
    """
    today = datetime.date.today()
    if "date" in request.GET:
        if re.match(_datePattern, request.GET['date']):
            tmp = request.GET['date'].split("-")
            date = today = datetime.date(int(tmp[0]), int(tmp[1]), int(tmp[2]))
    #to get to Monday, subtract the current day of the week from the date
    begin = today - datetime.timedelta(today.weekday())
    end = begin + datetime.timedelta(days=6);
    week = {'begin':begin, 'end':end}

    paperTeam = models.UserProfiles.objects.filter(team="paper")
    #Get all of the papers and datasets the user created for the week
    for u in paperTeam:
        u.allPapers = models.Papers.objects.filter(user=u.user)
        u.weekPapers = u.allPapers.filter(date_collected__gte=begin).filter(date_collected__lte=end)
        for p in u.weekPapers:
            p.datasets = models.Datasets.objects.filter(paper=p.id)

        u.allDatasets = models.Datasets.objects.filter(user=u.user)
        u.weekDatasets = u.allDatasets.filter(date_collected__gte=begin).filter(date_collected__lte=end)

        u.allHuman = u.allDatasets.filter(species__name="Homo Sapien")
        u.allMouse = u.allDatasets.filter(species__name="Mus Musculus")
        #categories - NOTE: how we SPAN relationships w/ __
        u.humanTF = u.allHuman.filter(factor__type="tf")
        u.humanHM = u.allHuman.filter(factor__type="hm")
        u.mouseTF = u.allMouse.filter(factor__type="tf")
        u.mouseHM = u.allMouse.filter(factor__type="hm")
        
    #dataTeam = models.UserProfiles.objects.filter(team="data")
    #The paper team can both create datasets and upload dataset data
    dataTeam = models.UserProfiles.objects.filter(Q(team="data") | Q(team="paper"))
    for u in dataTeam:
        u.allDatasets = models.Datasets.objects.filter(uploader=u.user)
        u.weekDatasets = u.allDatasets.filter(upload_date__gte=begin).filter(upload_date__lte=end)

        u.allHuman = u.allDatasets.filter(species__name="Homo Sapien")
        u.allMouse = u.allDatasets.filter(species__name="Mus Musculus")
        #categories
        u.humanTF = u.allHuman.filter(factor__type="tf")
        u.humanHM = u.allHuman.filter(factor__type="hm")
        u.mouseTF = u.allMouse.filter(factor__type="tf")
        u.mouseHM = u.allMouse.filter(factor__type="hm")

    return render_to_response('datacollection/report.html',
                              locals(),
                              context_instance=RequestContext(request))

@login_required
def teams(request):
    """A page to list the current teams and assign users to different teams"""
    return render_to_response('datacollection/teams.html',
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
    
@login_required
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
        return HttpResponseRedirect(reverse('datasets'))
    else:
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

# NOT USEFUL
# @login_required
# def batch_update_papers(request):
#     """See batch edit datasets--similar idea but for papers"""
#     title = "Batch Update Papers"
#     fields = forms.BatchUpdatePapersForm.Meta.fields
#     if request.method == "POST":
#         papers = [models.Papers.objects.get(pk=id) \
#                   for id in request.GET['papers'].split(',')]
#         for p in papers:
#             form = forms.BatchUpdatePaperForm(request.POST, instance=p)
#             if form.is_valid():
#                 tmp = form.save()
#         return HttpResponseRedirect(reverse('all_papers'))
#     else:
#         if 'papers' in request.GET:
#             paperList = request.GET['papers']
#             papers = [models.Papers.objects.get(pk=id)\
#                       for id in paperList.split(",")]
#             tmp = models.Papers()
#             for f in fields:
#                 #have to make exception for user b/c it can't be set to None
#                 if f == "user" and not _allSameOrNone(papers, f):
#                     setattr(tmp, f, auth.models.User.objects.get(pk=1))
#                 else:
#                     setattr(tmp, f, _allSameOrNone(papers, f))
#             form = forms.BatchUpdatePapersForm(instance=tmp)
#     return render_to_response('datacollection/batch_update_papers_form.html',
#                               locals(),
#                               context_instance=RequestContext(request))
            

def search(request):
    """the search page"""
    return render_to_response('datacollection/search.html',
                              locals(),
                              context_instance=RequestContext(request))

# @login_required
# def delete_datasets(request):
#     """Given a url param defining which datasets to delete, this view
#     tries to delete the datasets
#     """
#     if 'datasets' in request.GET:
#         datasets = request.GET['datasets']
#         dsets = [models.Datasets.objects.get(pk=id) \
#                  for id in datasets.split(',')]
#         for d in dsets:
#             d.delete()
#     return HttpResponseRedirect(reverse('datasets'))

# @login_required
# def delete_papers(request):
#     """Given a url param defining which papers to delete, this view
#     tries to delete the papers
#     """
#     if 'papers' in request.GET:
#         papers = [models.Papers.objects.get(pk=id) \
#                  for id in request.GET['papers'].split(',')]
#         for p in papers:
#             p.delete()
#     return HttpResponseRedirect(reverse('papers'))

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
    return login_required(generic_delete_view)

delete_datasets = delete_view_factory('datasets', models.Datasets, 'datasets')
delete_papers = delete_view_factory('papers', models.Papers, 'papers')
delete_samples = delete_view_factory('samples', models.Samples, 'samples')

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
    return render_to_response('datacollection/dcstats.html',
                              locals(),
                              context_instance=RequestContext(request))
@login_required
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
