from django.shortcuts import render_to_response
from django.contrib import auth
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
#from django.contrib.auth.views import login
import models
import forms
#import user
#import django.forms

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
            tmp = form.save() #will commit to the db
            return render_to_response('datacollection/foo.html', locals(),
                                      context_instance=RequestContext(request))
    else:
        form = forms.PaperForm()
    return render_to_response('datacollection/new_paper_form.html', locals(),
                              context_instance=RequestContext(request))

@login_required
def new_dataset_form(request):    
    if request.method == "POST":
        form = forms.DatasetForm(request.POST, request.FILES)
        if form.is_valid():
            tmp = form.save() #will commit to the db
            return render_to_response('datacollection/foo.html', locals(),
                                      context_instance=RequestContext(request))
    else:
        form = forms.DatasetForm()
    return render_to_response('datacollection/new_dataset_form.html', locals(),
                              context_instance=RequestContext(request))

# def login_view(request):
#     redirect_to = request.REQUEST.get('next','')
#     if not redirect_to:
#         request.GET["next"] = "/datasets/"
#     #if request.method == "GET":
#     #    if not 'next' in request.GET:
#     #        request.GET["next"] = "/datasets/"
#    login(request)

def datasets(request):
    """View all of the datasets in an excel like table"""
    datasets = models.Datasets.objects.all()
    return render_to_response('datacollection/datasets.html', locals(),
                              context_instance=RequestContext(request))
    
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/datasets/")
    else:
        form = UserCreationForm()
    return render_to_response("registration/register.html", locals(),
                              context_instance=RequestContext(request))
