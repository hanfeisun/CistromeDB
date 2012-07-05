from django import forms
import sys
import models
from new import classobj

#a trick to get the current module
_modname = globals()['__name__']
_this_mod = sys.modules[_modname]

# class PaperForm(forms.Form):
#     pmid = forms.IntegerField()
#     gseid = forms.CharField()
#     title = forms.CharField()
#     abstract = forms.CharField(widget=forms.Textarea)
#     pub_date = forms.DateField()
#     last_auth = forms.CharField()
#     last_auth_email = forms.EmailField()

# class PaperForm(forms.ModelForm):
#     class Meta:
#         model = models.Papers
#         exclude = ('date_collected', 'user', 'status', 'comments')
#     labels = {'pmid':'Pubmed ID', 'gseid':'GEO Series ID',
#               'pub_date':'Publication Date',
#               #'last_auth':'Last Author',
#               #'last_auth_email': 'Last Author Email'
#               }
#     def __init__(self, post=None):
#         super(PaperForm, self).__init__(post)
#         for k in self.labels.keys():
#             self.fields[k].label = self.labels[k]


def FormFactory(name, model):
    return classobj(name, (forms.ModelForm,),
                    {'Meta': classobj('Meta',(),{'model':model})})

#we should iterate over the models and auto generate these
form_dict = {'Paper': models.Papers, 'Dataset': models.Datasets,
             'Platform': models.Platforms,
             'Factor': models.Factors, 'Celltype':models.CellTypes,
             'Cellline': models.CellLines, 'Cellpop':models.CellPops,
             'Strain': models.Strains, 'Condition':models.Conditions,
             'Journal': models.Journals, 'Species':models.Species,
             'Assembly': models.Assemblies, 'Sample':models.Samples,
             'Diseasestate': models.DiseaseStates, 
             'Tissuetype':models.TissueTypes}


for k in form_dict:
    #tmp = FormFactory(k+'Form', form_dict[k])
    #HACK! instead of PlatformForm = ... we do this
    #WOW! this works!
    setattr(_this_mod, k+'Form',
            FormFactory(k+'Form', form_dict[k]))

#OVERWRITE our autogenerated one!
class PaperForm(forms.ModelForm):
    class Meta:
        model = models.Papers
        exclude = ('date_collected', 'user', 'status', 'comments')

class DatasetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DatasetForm, self).__init__(*args, **kwargs)
        #TURNING ManyToMany fields as TextInput
        self.fields['treats'].widget = forms.TextInput()
        self.fields['treats'].help_text = "example: [886L, 887L, 888L]"
        self.fields['conts'].widget = forms.TextInput()
        self.fields['conts'].help_text = "example: [886L, 887L, 888L]"
        
    class Meta:
        model = models.Datasets
        exclude = ("peak_file", "peak_xls_file", "summit_file", 
                   "treat_bw_file", "cont_bw_file", "conservation_file",
                   "conservation_r_file", "ceas_file", "ceas_r_file", 
                   "ceas_xls_file", "venn_file", "seqpos_file", 
                   #WHY are these charfields??
                   "rep_treat_bw", "rep_treat_peaks", 
                   "rep_treat_summits", "rep_cont_bw", 
                   #END WHY
                   "cor_pdf_file", "cor_r_file", "conf_file", "log_file", 
                   "summary_file", "dhs_file",
                   #NOTE: following fields should be removed from the model
                   "treatments", "controls")

class SampleForm(forms.ModelForm):
    class Meta:
        model = models.Samples
        exclude = ('user', 'paper', 'treatments', 'controls')

#Used by the data team to upload dataset files
class UploadDatasetForm(forms.ModelForm):
    class Meta:
        model = models.Datasets
        #NOTE: for some reason fields isn't working, try exclude instead
        fields = ('raw_file', 'treatment_file', 'peak_file', 'wig_file',
                  'bw_file',
                  )
        exclude = tuple([f.name for f in model._meta.fields \
                         if f.name not in fields])
        #exclude = ('gsmid', 'name', 'chip_page', 'control_gsmid',
        #           'control_page', 'date_collected', 'raw_file_url',
        #           'raw_file_type', 'user', 'paper', 'factor', 'platform',
        #           'species', 'assembly', 'description', 'cell_type',
        #           'cell_line', 'cell_pop', 'strain', 'condition', 'status',
        #           'comments', 'uploader', 'upload_date')

#We want full control over ALL fields for the update forms
class UpdatePaperForm(forms.ModelForm):
    class Meta:
        model = models.Papers

class UpdateDatasetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UpdateDatasetForm, self).__init__(*args, **kwargs)
        #TURNING ManyToMany fields as TextInput
        self.fields['treats'].widget = forms.TextInput()
        self.fields['treats'].help_text = "example: [886L, 887L, 888L]"
        self.fields['conts'].widget = forms.TextInput()
        self.fields['conts'].help_text = "example: [886L, 887L, 888L]"

    class Meta:
        model = models.Datasets
        #Don't include the files--use the Upload form for that
        exclude = DatasetForm.Meta.exclude
    
    #NOTE: if you get validating errs, you can override the validators like
    # def clean_raw_file_type(self):
    #      """IF we don't define this, it complains that the ftp:// URLS
    #      we give are invalid
    #      """
    #      cleaned_data = self.cleaned_data["raw_file_type"]
    #      #raise forms.ValidationError("FOOBAR!")
    #      return cleaned_data

class UpdateSampleForm(forms.ModelForm):
    class Meta:
        model = models.Samples
        fields = ('user', 'paper', 'treatments', 'controls', 
                  'uploader', 'upload_date',
                  'status', 'comments')
        exclude = tuple([f.name for f in model._meta.fields \
                         if f.name not in fields])

class BatchUpdateDatasetsForm(forms.ModelForm):
    class Meta:
        model = models.Datasets
        fields = ('paper', 'factor', 'platform', 'species', 'assembly', 
                  'cell_type', 'cell_line',
                  'cell_pop', 'strain', 'condition', 'disease_state',
                  'status', 'comments',
                  'user', 'uploader', 'curator', 'description',)
        exclude = tuple([f.name for f in model._meta.fields \
                         if f.name not in fields])

#realized that this doesn't have much usefulness
# class BatchUpdatePapersForm(forms.ModelForm):
#     class Meta:
#         model = models.Papers
#         fields = ('user',
#                   'title', 'abstract', 'pub_date',
#                   'date_collected', 'authors', 'last_auth_email',
#                   'journal', 'status', 'comments')
#         exclude = tuple([f.name for f in model._meta.fields \
#                          if f.name not in fields])
