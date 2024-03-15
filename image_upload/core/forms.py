from django import forms
from .models import Uploaded_Image
from splitjson.widgets import SplitJSONWidget
import json

 


class ImageForm(forms.ModelForm):
 
    class Meta:
        model = Uploaded_Image
        fields = ['image']
       

class ResultsForm(forms.Form):
    
    attrs = {'class': 'special', 'size': '80'}
    data = forms.CharField(widget=SplitJSONWidget(attrs=attrs))


class ImageMetaDataForm(forms.Form):
    def __init__(self, field_list, json_data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if json_data:
            for field_name in field_list:
                initial_value = json_data.get(field_name, '')  # Get the value from JSON data or set default ''
                self.fields[field_name] = forms.CharField(initial=initial_value, required=False)
    
         # Add description field
