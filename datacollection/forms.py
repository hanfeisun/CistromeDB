from django import forms
import models

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
              'pub_date':'Publication Date', 'last_auth':'Last Author',
              'last_auth_email': 'Last Author Email'}
    def __init__(self, post=None):
        super(PaperForm, self).__init__(post)
        for k in self.labels.keys():
            self.fields[k].label = self.labels[k]

class DatasetForm(forms.ModelForm):
    class Meta:
        model = models.Datasets

