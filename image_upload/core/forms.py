from django import forms
from .models import Uploaded_Image
 
 
class ImageForm(forms.ModelForm):
 
    class Meta:
        model = Uploaded_Image
        fields = ['image']