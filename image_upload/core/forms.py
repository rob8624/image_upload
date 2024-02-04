from django import forms
from .models import Uploaded_Image
from splitjson.widgets import SplitJSONWidget

 


class ImageForm(forms.ModelForm):
 
    class Meta:
        model = Uploaded_Image
        fields = ['image']
       

class ResultsForm(forms.Form):
    
    attrs = {'class': 'special', 'size': '40'}
    data = forms.CharField(widget=SplitJSONWidget(attrs=attrs, debug=True))


