from django.shortcuts import render, redirect, HttpResponse
import subprocess
from .forms import ImageForm, ResultsForm, ImageMetaDataForm
from .models import Uploaded_Image
from django.core.files.images import ImageFile
from PIL import Image as PILImage
from PIL.ExifTags import TAGS

import json 

from pyexif import pyexif
from exif import Image
import tempfile

from PIL import Image as PillowImage
from PIL import ExifTags
import exiftool


def all_data(image_path, selection):
    with exiftool.ExifToolHelper() as et:
        return(et.execute_json(image_path,  "-j"))
    
def iptc_data(image_path, selection):
    with exiftool.ExifToolHelper() as et:
        return(et.execute_json(image_path, "-IPTC:all",  "-j"))
    

def xmp_data(image_path, selection):
    with exiftool.ExifToolHelper() as et:
        return(et.execute_json(image_path, "-XMP:all",  "-j"))





def extract_exif_data(image_path, selection):
    if selection:
        
        return json.loads((subprocess.check_output(["exiftool", f"-{selection}:all",  image_path, "-g",  "-j", ])))
    else:
        return json.loads((subprocess.check_output(["exiftool", image_path,  "-j", ])))



def write_exif_data(image_path, data):
    with exiftool.ExifToolHelper() as et:
        print(image_path)
        print("writing data.....")
        return(et.execute(image_path,  f"-j={data}"))
    
    #print(data)
    #return subprocess.check_output(["exiftool", image_path, f"-j={data}" ])



def clean_data_from_request(request):
    cleaned_data = {
        key.replace('data__', ''): value if not isinstance(value, list) else value[0]
        for key, value in request.POST.items() if key.startswith('data__')
    }
    return cleaned_data



def upload(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        selection = request.POST.get('dataselect', None)
        print("select", selection)
        
        if form.is_valid():
            image = form.save()
            if selection == "iptc":
                exif_data_list  = iptc_data(image.image.path, selection)
            elif selection == "xmp":
                exif_data_list  = xmp_data(image.image.path, selection)
            else:
                exif_data_list  = all_data(image.image.path, selection)
            #exiftool function returns a list containing dict, this extracts the first element which is dict holding data
            if exif_data_list and isinstance(exif_data_list, list) and len(exif_data_list) == 1:
                exif_data_dict = exif_data_list[0]
                if "ExifToolVersion" in exif_data_dict:
                    exif_data_dict.pop("ExifToolVersion")
                
                # Assign the extracted exif data dictionary to the exif_data field
                image.exif_data = exif_data_dict
                image.save()
            return redirect('show_image', image_id=image.id, selection=selection)
    else:
        form = ImageForm()

    return render(request, 'core_upload.html', {'form': form})



def show_image(request, image_id, selection):
    try:
        image = Uploaded_Image.objects.get(id=image_id)
    except Uploaded_Image.DoesNotExist:
        return HttpResponse("Image not found", status=404)
    selection = selection.upper()
    if image.exif_data:
        
        image_exif_data = image.exif_data
       
        print("test", image_exif_data)
        if isinstance(image.exif_data, str):
            image_exif_data = json.loads(image.exif_data)
        else:
            pass
    image.save()
    return render(request, 'image_result.html', {'image': image, 'image_exif_data': image_exif_data, 'selection': selection, 'form': ImageForm()})


def test_view(request, image_id):
    sumbmitted = False
    #gets an instance of uploaded_image
    image = Uploaded_Image.objects.get(id=image_id)
    
    #creates a empty dict to hold the exif
    image_exif_data = {}
    #get data from the exif_data table (extracted in previous view) and convert to JSON. 
    if image.exif_data:
        if isinstance(image.exif_data, str):
            image_exif_data = json.loads(image.exif_data)
        else:
            image_exif_data = image.exif_data
    
    print(image_exif_data)
    
    #creat a instance of ResultsForm (forms.py) and prefill with image_exif_data
  
    form = ImageMetaDataForm(field_list=list(image_exif_data.keys()), json_data=image_exif_data)
    
   
     
    #if the sumbit but is clicked logic passes through this....
    #we check for the HTMX and HTMX trigger request.....
    
    if request.htmx and request.htmx.trigger == "edit-data":
        
        
        cleaned_data = clean_data_from_request(request)
        print(cleaned_data)
        cleaned_data['SourceFile'] = "*"
        exif_data_str = json.dumps(request.POST)
        print(exif_data_str)
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(exif_data_str)
        temp_file_path = temp_file.name
        write_exif_data(image.image.path, temp_file_path)
        image.exif_data = exif_data_str      
        image.save()   
        sumbmitted = True
        return render(request, 'data_template.html', {'form': cleaned_data, 'new_image': image})
            
        
        
    
    print("not htmx")  
    return render(request, 'test_template.html', {'form': form, 'image': image,  })












