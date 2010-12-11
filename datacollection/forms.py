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

class PaperForm(forms.ModelForm):
    class Meta:
        model = models.Papers
    labels = {'pmid':'Pubmed ID', 'gseid':'GEO Series ID',
              'pub_date':'Publication Date',
              #'last_auth':'Last Author',
              #'last_auth_email': 'Last Author Email'
              }
    def __init__(self, post=None):
        super(PaperForm, self).__init__(post)
        for k in self.labels.keys():
            self.fields[k].label = self.labels[k]

# class DatasetForm(forms.ModelForm):
#     class Meta:
#         model = models.Datasets

#SHOULD write a class generator!
# class PlatformForm(forms.ModelForm):
#     class Meta:
#         model = models.Platforms

def FormFactory(name, model):
    return classobj(name, (forms.ModelForm,),
                    {'Meta': classobj('Meta',(),{'model':model})})

#we should iterate over the models and auto generate these
form_dict = {'Dataset': models.Datasets, 'Platform': models.Platforms,
             'Factor': models.Factors, 'Celltype':models.CellTypes,
             'Cellline': models.CellLines, 'Cellpop':models.CellPops,
             'Strain': models.Strains, 'Condition':models.Conditions,
             'Journal': models.Journals}


for k in form_dict:
    #tmp = FormFactory(k+'Form', form_dict[k])
    #HACK! instead of PlatformForm = ... we do this
    #WOW! this works!
    setattr(_this_mod, k+'Form',
            FormFactory(k+'Form', form_dict[k]))
