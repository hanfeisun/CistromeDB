import os
import sys
import datetime
import subprocess
import re

from django.shortcuts import render_to_response, Http404, get_object_or_404
from django.contrib import auth
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect, HttpResponse
#from django.contrib.auth.views import login
from django.core.urlresolvers import reverse

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

def no_view(request):
    """
    We don't really want anyone going to the static_root.
    However, since we're raising a 404, this allows flatpages middleware to
    step in and serve a page, if there is one defined for the URL.
    """
    raise Http404

def papers(request):
    papers = models.Papers.objects.all()
    return render_to_response('datacollection/papers.html', locals(),
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
            return HttpResponseRedirect(reverse('home'))
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
            return HttpResponseRedirect(reverse('home'))
        else:
            print "INVALID DATASET FORM"
    else:
        form = forms.DatasetForm()
        #NOTE: we can't pass in the param as paper b/c when we post, it
        #clobbers the hidden input in our form
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
def new_replicate_form(request):
    if request.method == "POST":
        form = forms.ReplicateForm(request.POST, request.FILES)
        if form.is_valid():
            tmp = form.save(commit=False)
            tmp.user = request.user
            #I'm not sure why the form isn't finding paper OR datasets in
            #request.POST
            tmp.datasets = request.POST['datasets']
            tmp.paper = models.Papers.objects.get(id=request.POST['paper'])
            tmp.save()
            return HttpResponseRedirect(reverse('home'))
        else:
            print "INVALID REPLICATE FORM"
    else:
        form = forms.ReplicateForm()
        if 'p' in request.GET:
            paper = request.GET['p']
    return render_to_response('datacollection/new_replicate_form.html',
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
generic_update_list = generic_forms_list + ['paper']
for name in generic_update_list:
    form = getattr(forms, "%sForm" % name.capitalize())
    tmp_view = update_form_factory('%s Update Form' % name.capitalize(), form)
    setattr(_this_mod, "update_%s_form" % name.lower(), tmp_view)
#------------------------------------------------------------------------------

def all_papers(request, user_id):
    """If given a user_id, shows all of the papers imported by the user,
    otherwise shows all papers in the db"""

    if user_id:
        #NOTE: the current url regex doesn't parse out the / from the user_id
        if user_id.endswith("/"):
            user_id = user_id[:-1]
        papers = models.Papers.objects.filter(user=user_id)
    else:
        papers = models.Papers.objects.all()
    #papersList = "[%s]" % ",".join(map(lambda p: p.to_json(), papers))
    return render_to_response('datacollection/all_papers.html', locals(),
                              context_instance=RequestContext(request))

def weekly_papers(request, user_id):
    """Returns all of the papers that the user worked on since the given date,
    IF date is not given as a param, then assumes date = beginning of the week
    """
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
        
    return render_to_response('datacollection/all_papers.html', locals(),
                              context_instance=RequestContext(request))

def datasets(request, user_id):
    """View all of the datasets in an excel like table; as with all_papers
    if given a user_id, it will return a page of all of the datsets collected
    by the user
    """
    if user_id:
        if user_id.endswith("/"):
            user_id = user_id[:-1]
        datasets = models.Datasets.objects.filter(user=user_id)
    else:
        datasets = models.Datasets.objects.all()
    return render_to_response('datacollection/datasets.html', locals(),
                              context_instance=RequestContext(request))

def weekly_datasets(request, user_id):
    """Returns all of the datasets that the user worked on since the given date
    IF date is not given as a param, then assumes date = beginning of the week
    """
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

@login_required
def auto_paper_import(request):
    """View of auto_paper importer where curators can try to fetch GEO
    information using pubmed ids"""
    if request.method == "POST":
        #the user is trying to autoimport a paper
        if request.POST['gseid']:
            geoQuery = entrez.PaperAdapter(request.POST['gseid'])
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
            tmp.user = request.user
            tmp.date_collected = datetime.datetime.now()

            tmp.save()
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
    replicates = models.Replicates.objects.filter(paper=paper_id)
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
    return render_to_response('datacollection/dataset_profile.html',
                              locals(),
                              context_instance=RequestContext(request))

def replicate_profile(request, replicate_id):
    """View of the paper_profile page"""
    replicate = models.Replicates.objects.get(id=replicate_id)
    dsets = replicate.datasets.split(",")
    datasets = [models.Datasets.objects.get(id=d) for d in dsets]
    return render_to_response('datacollection/replicate_profile.html',
                              locals(),
                              context_instance=RequestContext(request))

@login_required
def report(request):
    """Generates the weekly report page"""
    today = datetime.date.today()
    #to get to Monday, subtract the current day of the week from the date
    begin = today - datetime.timedelta(today.weekday())
    end = begin + datetime.timedelta(days=6);
    week = {'begin':begin, 'end':end}

    paperTeam = models.UserProfiles.objects.filter(team="paper")
    #Get all of the papers and datasets the user created for the week
    for u in paperTeam:
        u.allPapers = models.Papers.objects.filter(user=u.user)
        u.weekPapers = u.allPapers.filter(date_collected__gte=begin)

        u.allDatasets = models.Datasets.objects.filter(user=u.user)
        u.weekDatasets = u.allDatasets.filter(date_collected__gte=begin)
        
    dataTeam = models.UserProfiles.objects.filter(team="data")
    for u in dataTeam:
        u.allDatasets = models.Datasets.objects.filter(uploader=u.user)
        u.weekDatasets = u.allDatasets.filter(upload_date__gte=begin)
        

    return render_to_response('datacollection/report.html',
                              locals(),
                              context_instance=RequestContext(request))

@login_required
def teams(request):
    """A page to list the current teams and assign users to different teams"""
    return render_to_response('datacollection/teams.html',
                              locals(),
                              context_instance=RequestContext(request))
