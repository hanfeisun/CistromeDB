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
    papers = models.Papers.objects.order_by('-date_collected')[:10]
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

@admin_only
#def new_dataset_form(request):
def new_sample_form(request):
    if request.method == "POST":
        form = forms.SampleForm(request.POST, request.FILES)
        if form.is_valid():
            tmp = form.save(commit=False)
            tmp.date_collected = datetime.datetime.now()
            tmp.user = request.user
            #I'm not sure why the form isn't finding paper in request.POST
            tmp.paper = models.Papers.objects.get(id=request.POST['paper'])
            tmp.save()
            return HttpResponseRedirect(request.POST['next'])
        else:
            print "INVALID SAMPLE FORM"
    else:
        form = forms.SampleForm()
        #NOTE: we can't pass in the param as paper b/c when we post, it
        #clobbers the hidden input in our form
        if 'next' in request.GET:
            next = request.GET['next']
        if 'p' in request.GET:
            #paper = models.Papers.objects.get(id=request.GET['paper'])
            paper = request.GET['p']
    return render_to_response('datacollection/new_sample_form.html', locals(),
                              context_instance=RequestContext(request))

@admin_only
#def new_sample_form(request):
def new_dataset_form(request):
    if request.method == "POST":
        tmp = models.Datasets()
        tmp.user = request.user
        tmp.treatments = request.POST['treatments']
        tmp.controls = request.POST['controls']
        tmp.paper = models.Papers.objects.get(id=request.POST['paper'])
        tmp.save()
        return HttpResponseRedirect(request.POST['next'])
    else:
        form = forms.DatasetForm()
        if 'next' in request.GET:
            next = request.GET['next']
        if 'p' in request.GET:
            paper = request.GET['p']
    return render_to_response('datacollection/new_dataset_form.html',
                              locals(),
                              context_instance=RequestContext(request))

@admin_only
#def upload_dataset_form(request, sample_id):
def upload_sample_form(request, sample_id):
    """Given a sample_id, generate or handle a form that will allow users
    to upload the files associated with it
    """
    if request.method == "POST":
        sample = models.Samples.objects.get(pk=sample_id)
        #we want to only update the record, not add a new one--hence instance
        form = forms.UploadSampleForm(request.POST, request.FILES,
                                       instance=sample)
        if form.is_valid():
            tmp = form.save(commit=False)
            tmp.upload_date = datetime.datetime.now()
            tmp.uploader = request.user
            tmp.save()
            return HttpResponseRedirect(request.POST['next'])
        else:
            print "INVALID UPLOAD SAMPLE FORM"
    else:
        form = forms.UploadSampleForm()
        if 'next' in request.GET:
            next = request.GET['next']
    return render_to_response('datacollection/upload_sample_form.html',
                              locals(),
                              context_instance=RequestContext(request))
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
                      'strain', 'condition', 'journal', 'species', 'filetype',
                      'assembly', "diseasestate", "control"]
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

#Generic Batch Update section HERE!

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

@admin_only
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
    paginator = Paginator(papers, _items_per_page) #25 items per page
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

        paginator = Paginator(papers, _items_per_page) #25 items per page
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        try:
            pg = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pg = paginator.page(paginator.num_pages)

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

#a nice fn, but overkill for what we need...i'm going to leave it around for
#inspiration
def _aggregateFiles(model_obj_list, add_to_obj=False):
    """Given a list of model objects, whose models have FileFields, introspects
    the obj and returns the FileFields of each obj as a list; 
    uses the first object to introspect the model **SO WE ASSUME that 
    the objects are of the same type**
    if add_to_obj, then adds the filefields to the the obj as _fileFields"""
    def getFileFields(self):
        return self._fileFields

    if len(model_obj_list) > 0:
        #try to find the FileFields via introspection
        fflds = [f.name for f in model_obj_list[0]._meta.fields \
                     if isinstance(f, FileField)]
        tmp = []
        for o in model_obj_list:
            foo = [getattr(o, f) for f in fflds]
            if add_to_obj:
                setattr(o, "_fileFields", foo)
                #ADD getFileFields as an instance method b/c we can't access
                #_fileFields in the templates!
                setattr(o.__class__, "getFileFields", getFileFields)
            tmp.append(foo)
        return tmp
    else:
        return []    

def _getFileFields(model_obj_list):
    """Given a list of model objects, whose models have FileFields, introspects
    the obj and returns the FileFields of the Model
    uses the first object to introspect the model **SO WE ASSUME that 
    the objects are of the same type**
    inspired by _aggregateFiles"""
    if len(model_obj_list) > 0:
        #try to find the FileFields via introspection
        fflds = [f.name for f in model_obj_list[0]._meta.fields \
                     if isinstance(f, FileField)]
        return fflds
    else:
        return [] 


#NOTE: i sould cache these!!
@admin_only
#def datasets(request, user_id):
def samples(request, user_id):
    """View all of the samples in an excel like table; as with papers
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
            samples = models.Samples.objects.filter(uploader=user_id)
        else:
            samples = models.Samples.objects.filter(user=user_id)
    else:
        samples = models.Samples.objects.all()

    #control things w/ paginator
    #ref: http://docs.djangoproject.com/en/1.1/topics/pagination/
    paginator = Paginator(samples, _items_per_page) #25 items per page
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        pg = paginator.page(page)
    except (EmptyPage, InvalidPage):
        pg = paginator.page(paginator.num_pages)

    #prepare the fileFields for the Files col--note we do it here for efficien.
    ignored = _aggregateFiles(pg.object_list, add_to_obj=True)
        
    return render_to_response('datacollection/samples.html', locals(),
                              context_instance=RequestContext(request))

#NOTE: i sould cache these!!
@admin_only
def controls(request):
    """View all of the controls in an excel like table
    """
    controls = models.Controls.objects.all()
    current_path = request.get_full_path()

    #control things w/ paginator
    #ref: http://docs.djangoproject.com/en/1.1/topics/pagination/
    paginator = Paginator(controls, _items_per_page) #25 items per page
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        pg = paginator.page(page)
    except (EmptyPage, InvalidPage):
        pg = paginator.page(paginator.num_pages)

    #prepare the fileFields for the Files col--note we do it here for efficien.
    ignored = _aggregateFiles(pg.object_list, add_to_obj=True)
        
    return render_to_response('datacollection/controls.html', locals(),
                              context_instance=RequestContext(request))


@admin_only
#def weekly_datasets(request, user_id):
def weekly_samples(request, user_id):
    """Returns all of the samples that the user worked on since the given date
    IF date is not given as a param, then assumes date = beginning of the week
    IF a url param uploader is given, then we use uploader instead of user to
    get the samples
    IF NO user_id is given, returns a page allowing the user to select which
    user to view
    """
    if user_id:
        #NOTE: the current url regex doesn't parse out the / from the user_id
        if user_id.endswith("/"):
            user_id = user_id[:-1]
        if 'uploader' in request.GET:
            samples = models.Samples.objects.filter(uploader=user_id)
        else:
            samples = models.Samples.objects.filter(user=user_id)
        today = datetime.date.today()
        begin = today - datetime.timedelta(today.weekday())
        if "date" in request.GET:
            if re.match(_datePattern, request.GET['date']):
                tmp = request.GET['date'].split("-")
                d = datetime.date(int(tmp[0]), int(tmp[1]), int(tmp[2]))
            else:
                d = begin
            samples = samples.filter(date_collected__gte=d)
        else:
            #No date param, take the beginning of the week
            samples = samples.filter(date_collected__gte=begin)

        #control things w/ paginator
        #ref: http://docs.djangoproject.com/en/1.1/topics/pagination/
        paginator = Paginator(samples, _items_per_page) #25 items per page
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
    else:
        #list users
        title = "Weekly Samples"
        users = auth.models.User.objects.all()
        url = reverse('weekly_samples')
        return render_to_response('datacollection/list_users.html', locals(),
                                  context_instance=RequestContext(request))

#def get_datasets(request, paper_id):
def get_samples(request, paper_id):
    """return all of the samples associated w/ paper_id in json
    Fields: gsmid, *platform, (platform)experiment_type, *species,
    factor, *cell_type, file
    * means that if it is set to 0, then inherit the paper's information
    """
    paper = models.Papers.objects.get(id=paper_id)
    samples = models.Samples.objects.filter(paper=paper_id)
    
    slist = ",".join([jsrecord.views.jsonify(s) for s in samples])
    return HttpResponse("[%s]" % slist)

@admin_only
#def samples(request):
def datasets(request):
    """Returns all of the datasets
    """
    datasets = models.Datasets.objects.all()

    #note: we have to keep track of these URL params so that we can feed them
    #into the paginator, e.g. if we click on platform=1, then when we paginate
    #we want the platform param to be carried through
    rest = ""
    if 'species' in request.GET:
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
    
    #here is where we order things by paper and then gsmid for the admins
    datasets = datasets.order_by("paper")

    def getsample_gsmid(sid):
        try:
            tmp = models.Samples.objects.get(pk=sid)
            return tmp.gsmid
        except:
            return sid
    for d in datasets:
        d.treatments_gsmid = map(getsample_gsmid, d.treatments.split(",")) \
            if d.treatments else []
        d.controls_gsmid = map(getsample_gsmid, d.controls.split(",")) \
            if d.controls else []

    paginator = Paginator(datasets, _items_per_page) #25 items per page
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        pg = paginator.page(page)
    except (EmptyPage, InvalidPage):
        pg = paginator.page(paginator.num_pages)

    #prepare the fileFields for the Files col--note we do it here for efficien.
    ignored = _aggregateFiles(pg.object_list, add_to_obj=True)

    return render_to_response('datacollection/datasets.html', locals(),
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

def _import_paper(pmid, user):
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
    return render_to_response('datacollection/dataset_profile.html',
                              locals(),
                              context_instance=RequestContext(request))

@admin_only
def sample_profile(request, sample_id):
    """View of the paper_profile page"""
    sample = models.Samples.objects.get(id=sample_id)
    # try:
    #     summary = models.DhsStats.objects.get(dataset=dataset)
    # except:
    #     pass
    return render_to_response('datacollection/sample_profile.html',
                              locals(),
                              context_instance=RequestContext(request))

@admin_only
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
    #Get all of the papers and samples the user created for the week
    for u in paperTeam:
        u.allPapers = models.Papers.objects.filter(user=u.user)
        u.weekPapers = u.allPapers.filter(date_collected__gte=begin).filter(date_collected__lte=end)
        for p in u.weekPapers:
            p.samples = models.Samples.objects.filter(paper=p.id)

        u.allSamples = models.Samples.objects.filter(user=u.user)
        u.weekSamples = u.allSamples.filter(date_collected__gte=begin).filter(date_collected__lte=end)
        
        # NOTE: species has moved to Datasets!!! removing this for now
        # u.allHuman = u.allSamples.filter(species__name="Homo Sapien")
        # u.allMouse = u.allSamples.filter(species__name="Mus Musculus")
        # #categories - NOTE: how we SPAN relationships w/ __
        # u.humanTF = u.allHuman.filter(factor__type="tf")
        # u.humanHM = u.allHuman.filter(factor__type="hm")
        # u.mouseTF = u.allMouse.filter(factor__type="tf")
        # u.mouseHM = u.allMouse.filter(factor__type="hm")
        
    #dataTeam = models.UserProfiles.objects.filter(team="data")
    #The paper team can both create samples and upload sample data
    dataTeam = models.UserProfiles.objects.filter(Q(team="data") | Q(team="paper"))
    for u in dataTeam:
        u.allSamples = models.Samples.objects.filter(uploader=u.user)
        u.weekSamples = u.allSamples.filter(upload_date__gte=begin).filter(upload_date__lte=end)

        # NOTE: species has moved to Datasets!!! removing this for now
        # u.allHuman = u.allSamples.filter(species__name="Homo Sapien")
        # u.allMouse = u.allSamples.filter(species__name="Mus Musculus")
        # #categories
        # u.humanTF = u.allHuman.filter(factor__type="tf")
        # u.humanHM = u.allHuman.filter(factor__type="hm")
        # u.mouseTF = u.allMouse.filter(factor__type="tf")
        # u.mouseHM = u.allMouse.filter(factor__type="hm")

    return render_to_response('datacollection/report.html',
                              locals(),
                              context_instance=RequestContext(request))

@admin_only
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

@admin_only
def batch_update_samples(request):
    """A page that allows the user to make batch updates to a set of samples.
    the samples are specified in the 'samples' url
    """
    title = "Batch Update Samples"
    fields = forms.BatchUpdateSamplesForm.Meta.fields
    if request.method == "POST":
        samples = [models.Samples.objects.get(pk=id) \
                       for id in request.GET['samples'].split(',')]
        for s in samples:
            form = forms.BatchUpdateSamplesForm(request.POST, instance=s)
            if form.is_valid():
                tmp = form.save()
        return HttpResponseRedirect(request.POST['next'])
    else:
        if 'next' in request.GET:
            next = request.GET['next']
        if 'samples' in request.GET:
            samp = request.GET['samples']
            samples = [models.Samples.objects.get(pk=sid) \
                           for sid in samp.split(',')]
            tmp = models.Samples()
            for f in fields:
                setattr(tmp, f, _allSameOrNone(samples, f))
            form = forms.BatchUpdateSamplesForm(instance=tmp)
    return render_to_response('datacollection/batch_update_samples_form.html',
                              locals(),
                              context_instance=RequestContext(request))

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
def _check_for_files(dataset):
    """Checks to make sure that the raw files associated for each of the 
    dataset's sample is present.
    Returns a list of samples whose raw files are missing; [] means the 
    dataset's files are all there!
    """
    missing_files_list = []

    samples = [models.Samples.objects.get(pk=sid) \
                    for sid in dataset.treatments.split(",")]
    
    if dataset.controls:
        samples.extend([models.Samples.objects.get(pk=sid) \
                             for sid in dataset.controls.split(",")])

    for s in samples:
        #check db entry
        if not s.raw_file:
            missing_files_list.append(int(s.id))
        #check file existence
        elif not os.path.exists(s.raw_file.path):
            missing_files_list.append(s.raw_file.path)
    
    return missing_files_list
    

@admin_only
def check_raw_files(request, dataset_id):
    """If the dataset's status is 'new', checks to see if that the raw files
    are uploaded/loaded for all of the samples assoc. w/ the dataset
    IF this condition holds, changes the status to 'checked', 
    OTHERWISE the status is 'error' and a msg is appended to comments
    """
    dataset = models.Datasets.objects.get(pk=dataset_id)
    page = 1
    if "page" in request.GET:
        page = request.GET['page']

    if dataset.status == "new":
        missing_files_list = _check_for_files(dataset)

        if missing_files_list: #some missing files-->ERROR
            dataset.status = "error"
            dataset.comments = "Samples %s are missing files" % \
                missing_files_list
            dataset.save()
        else:
            #No err!
            dataset.status = "checked"
            dataset.save()

    #redirect to the datasets view
    return HttpResponseRedirect(reverse('datasets')+("?page=%s" % page))

@admin_only
def run_analysis(request, dataset_id):
    """
    Tries to: 
    0. runs to make sure that all datasets have their files
       (redundant w/ check raw files)
    1. calls pipeline runner script on the dataset
    
    BLAH! more here! but later!
    """
    dataset = models.Datasets.objects.get(pk=dataset_id)
    page = 1
    if "page" in request.GET:
        page = request.GET['page']

    missing_files_list = _check_for_files(dataset)
    if missing_files_list:
        dataset.status = "error"
        dataset.comments = "Samples %s are missing files" % \
            missing_files_list
        dataset.save()
        return HttpResponseRedirect(reverse('datasets')+("?page=%s" % page))
    else: # ok to proceed!
        cwd = os.getcwd()
        working_dir = os.path.join(settings.MEDIA_ROOT, "data", "tmp", 
                                   "dataset%s" % dataset.id)
        #if not os.path.exists(working_dir):
            #os.mkdir(working_dir)
            #os.chdir(working_dir)
        conf_f = ConfGenerator.generate(dataset,request.user,working_dir,False)
        run_sh = RunSHGenerator.generate(dataset, conf_f, request.user,
                                         working_dir)

        # run the script as a daemon
        proc = subprocess.Popen(["python", "daemonize.py"], cwd=working_dir)
        
        dataset.status = "running"
        dataset.save()

    #redirect to the datasets view
    return HttpResponseRedirect(reverse('datasets')+("?page=%s" % page))


@admin_only
#def download_file(request, dataset_id):
def download_file(request, sample_id):
    """Tries to download the file for the given sample"""
    sample = models.Samples.objects.get(pk=sample_id)

    page = 1
    if "page" in request.GET:
        page = request.GET['page']

    #do the stuff here!
    #pattern: ftp://(server) (path) (file)
    #NOTE: this pattern may be buggy!
    url_pattern = "^ftp://((\w|-)+\.?)+(/(\w|-)+)*(/((\w|-)+\.)*\w+)$"
    if not re.match(url_pattern, sample.raw_file_url):
        sample.status = "error"
        sample.comments = "The file_url %s is invalid" % sample.raw_file_url
        sample.save()
        return HttpResponseRedirect(reverse('samples')+("?page=%s" % page))
    else: # ok to proceed!
        cwd = os.getcwd()
        working_dir = os.path.join(settings.MEDIA_ROOT, "data", "tmp", 
                                   "sample%s" % sample.id)
        dnld_sh = DnldSHGenerator.generate(sample, request.user, working_dir)
        proc = subprocess.Popen(["python", "daemonize.py"], cwd=working_dir)
        
    sample.status = "transfer" 
    sample.save()

    #redirect to the samples view
    return HttpResponseRedirect(reverse('samples')+("?page=%s" % page))

def _auto_sample_import(paper, user, gsmids):
    """Given a paper id and a set of gsmids, this fn tries to create the
    samples and associate it with the paper
    NOTE: we are also adding a check for the samples to see if they're 
    already in the system
    """

    for gsmid in gsmids:
        #check if the sample already exists
        (tmp, created) = models.Samples.objects.get_or_create(gsmid=gsmid, defaults={"date_collected": datetime.datetime.now(), "user":user, "paper":paper})
        if created:
            geoQuery = entrez.SampleAdapter(gsmid)
        
            attrs = ['gsmid', 'name', 'raw_file_url']
            for a in attrs:
                setattr(tmp, a, getattr(geoQuery, a))

            (tmp.raw_file_type, ignored) = models.FileTypes.objects.get_or_create(name=geoQuery.raw_file_type)

            platform = entrez.PlatformAdapter(geoQuery.platform)
            (tmp.platform, ignored) = models.Platforms.objects.get_or_create(gplid=platform.gplid, name=platform.name, technology=platform.technology)
            (tmp.species, ignored) = models.Species.objects.get_or_create(name=geoQuery.species)
            tmp.save()

@admin_only
def import_samples(request, paper_id):
    """Tries to import the samples associated with the paper.
    NOTE: before we returned JSON, but now we are making it more action-btn 
    like check_raw_files, run_analysis, etc
    """
    paper = models.Papers.objects.get(pk=paper_id)
    geoQuery = entrez.PaperAdapter(paper.pmid)
    _auto_sample_import(paper, paper.user, geoQuery.samples)
    
    page = 1
    if "page" in request.GET:
        page = request.GET['page']

    paper.status = "primed"
    paper.save()

    #redirect to the papers view
    return HttpResponseRedirect(reverse('papers')+("?page=%s" % page))

@admin_only
#def download_paper_datasets(request, paper_id):
def download_paper_samples(request, paper_id):
    """Tries to download the samples associated with the paper--calls the 
    download_sample fn
    """
    paper = models.Papers.objects.get(pk=paper_id)
    samples = models.Samples.objects.filter(paper=paper_id)

    page = 1
    if "page" in request.GET:
        page = request.GET['page']

    #call download_datasets but ignore the return
    for s in samples:
        #sending request is ok--b/c request.page doesn't really affect things
        ignored = download_file(request, s.id)

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
def modelPagesFactory(model, base_name):
    def generic_model_view(request):
        #model fields
        fields = [f.name for f in model._meta.fields]
        
        if (base_name != "species" and base_name != "assembly"):
            title = "%ss" % base_name.title()
        else:
            title = base_name.title()

        objs = model.objects.all()
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
                      "FileTypes",  "DiseaseStates", "Species",
                      #"Assemblies",
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
            modelPagesFactory(getattr(models, name), base_name))

assemblies = modelPagesFactory(models.Assemblies, "assembly")

#------------------------------------------------------------------------------
# search page
#------------------------------------------------------------------------------
#@cache_page(60 * 60 * 1)
def search(request):
    """This view takes a query param, q, and returns the jsonified records for
    all of the papers associated with that query string
    """
    #use paper ids to check for duplicates
    paper_ids = []
    tmp = []
    _timeout = 60*60*24 #1 day
    if 'q' in request.GET:
        key = request.GET['q']
        if cache.get(key):
            return HttpResponse(cache.get(key))

        res = SearchQuerySet().filter(content=key)
        for r in res:
            #NOTE: r.model, r.model_name, r.object
            if (r.model is models.Datasets) or (r.model is models.Samples):
                p = r.object.paper
            else:
                p = r.object

            if not p.id in paper_ids:
                paper_ids.append(p.id)
                #tmp.append(jsrecord.views.jsonify(p))
                tmp.append(p)

        #sort tmp by pub_date
        tmp.sort(key=lambda p: p.pub_date, reverse=True)
        tmp2 = [jsrecord.views.jsonify(p) for p in tmp]
        
        ret = "[%s]" % ",".join(tmp2)
        cache.set(key, ret, _timeout)
    #print paper_ids
    return HttpResponse(ret)

def front(request, rtype):
    """supports the front page retrieval of, for example, the most recent 
    papers (determined by rtype).
    returns JSON
    """
    _timeout = 60*60 #1 hr

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
