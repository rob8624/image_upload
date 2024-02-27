from django.shortcuts import render, redirect, HttpResponse
import subprocess
from .forms import ImageForm, ResultsForm
from .models import Uploaded_Image
from django.core.files.images import ImageFile
from PIL import Image as PILImage
from PIL.ExifTags import TAGS
import piexif
import pyexiv2
import json 
import pickle#
from pyexif import pyexif
from exif import Image
import tempfile

from PIL import Image as PillowImage
from PIL import ExifTags


# Create your views here.


def clean_data_from_request(request):
    cleaned_data = {
        key.replace('data__', ''): value if not isinstance(value, list) else value[0]
        for key, value in request.POST.items() if key.startswith('data__')
    }
    return cleaned_data



def upload(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        selection = request.POST.get('dataselect')
        
        
        if form.is_valid():
            image = form.save()
            exif_data_list  = extract_exif_data(image.image.path, selection)
            
            #exiftool function returns a list containing dict, this extracts the first element which is dict holding data
            if exif_data_list and isinstance(exif_data_list, list) and len(exif_data_list) == 1:
                exif_data_dict = exif_data_list[0]
                
                # Assign the extracted exif data dictionary to the exif_data field
                image.exif_data = exif_data_dict
                
                image.save()
            return redirect('show_image', image_id=image.id, selection=selection)
    else:
        form = ImageForm()

    return render(request, 'core_upload.html', {'form': form})



def show_image(request, image_id, selection=None):
    try:
        image = Uploaded_Image.objects.get(id=image_id)
    except Uploaded_Image.DoesNotExist:
        return HttpResponse("Image not found", status=404)
    
    if image.exif_data:
        image_exif_data = image.exif_data
    image.save()
    return render(request, 'image_result.html', {'image': image, 'image_exif_data': image_exif_data, 'selection':selection, 'form': ImageForm()})


def test_view(request, image_id):
    
    #gets an instance of uploaded_image
    image = Uploaded_Image.objects.get(id=image_id)
    
    #creates a empty dict to hold the exif
    image_exif_data = {}
    #get data from the exif_data table (extracted in previous view) and convert to JSON. 
    if image.exif_data:
        image_exif_data = image.exif_data
    
    #creat a instance of ResultsForm (forms.py) and prefill with image_exif_data
    form = ResultsForm(request.POST or None, initial={'data': image_exif_data})
    #if the sumbit but is clicked logic passes through this....
    #we check for the HTMX and HTMX trigger request.....
    if request.method == 'POST':
        if request.htmx and request.htmx.trigger == "edit-data":
            cleaned_data = clean_data_from_request(request)
            cleaned_data['SourceFile'] = "*"
            exif_data_str = json.dumps(cleaned_data)
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                temp_file.write(exif_data_str)
            temp_file_path = temp_file.name
            print(temp_file_path)
            print("dbdata", exif_data_str)
            write_exif_data(image.image.path, temp_file_path)
            
            image.exif_data = exif_data_str      
            image.save()   
            
            
           

        #    #converting to dicr with codes
        #     def get_exif_code(tag_name):
        #         for code, name in TAGS.items():
        #             if name == tag_name:
        #                 return code
        #         return None

        #     def convert_keys_to_exif_codes(data):
        #             return {get_exif_code(key): value for key, value in data.items() if value is not None}
            
        #     image_exif_data_with_codes = convert_keys_to_exif_codes(cleaned_data)
        #     print("CODES", image_exif_data_with_codes)
            
               
                
        #     bytes_valid_image_data = dict(
        #                 (k,v)
        #                 for (k,v) in image_exif_data_with_codes.items()
        #                 if (k is not None) and (v is not None)
        #                 )    
                                        
        #     valid_image_data = {key: value for key, value in bytes_valid_image_data.items() 
        #                         if not (isinstance(value, bytes) or (isinstance(value, str) 
        #                                                              and value.startswith("b'") and value.endswith("'")))}
        #     print("valid", valid_image_data)
            
            
           

        #     #ok lets try again#
        #     PILLOW_TAGS = valid_image_data.keys() 
                             
            
           
            
            
        #     VALUES = valid_image_data.values() 
            
        #     img = image.image.path
        #     edit_img = PILImage.open(img)
        #     exif_bytes = piexif.dump(img)
            
        #     zeroth_ifd = {piexif.ImageIFD.ImageDescription: image_exif_data_with_codes[270],
        #                 piexif.ImageIFD.Make: image_exif_data_with_codes[271],
        #                 piexif.ImageIFD.DateTime: image_exif_data_with_codes[306],
        #                 piexif.ImageIFD.Software: u"piexif"
        #                 }
        #     exif_dict = {"0th":zeroth_ifd}
        #     exif_bytes = piexif.dump(exif_dict)
        #     piexif.insert(exif_bytes, img)
        #     edit_img.save(image.image.path, exif=exif_bytes)
        #     print(exif_bytes)
        #     print("---------------------------")
        #     exif_dict = piexif.load(image.image.path)
        #     print(exif_dict)            
        #     image.save()
        #     new_image = image         
             
                
            
                   
                
            return render(request, 'data_template.html', {'form': cleaned_data, 'new_image': image})
            
        
            # exif_bytes = piexif.dump(test)
            # print(exif_bytes)
            # piexif.insert(exif_bytes, img)
    
    print("not htmx")  
    return render(request, 'test_template.html', {'form': form, 'image': image})








def extract_exif_data(image_path, selection):
    if selection:
        return json.loads((subprocess.check_output(["exiftool", f"-{selection}:all",  image_path,  "-j", ])))
    else:
        return json.loads((subprocess.check_output(["exiftool", image_path,  "-j", ])))



def write_exif_data(image_path, data):
    print("writing data.....")
    print(data)
    return subprocess.check_output(["exiftool", image_path, f"-j={data}" ])

    
    # try:
    #     with PILImage.open(image_path) as img:
    #         exif_data = {}
    #         for key in img._getexif():
    #             if key in TAGS and img._getexif()[key]:
    #                 exif_data[TAGS[key]] = img._getexif()[key]
    #         exif_data_json = json.dumps(exif_data, default=str)
    #         img.close()
    #         return exif_data_json
    # except Exception as e:
    #     print(f"Error extracting EXIF data from {image_path}: {e}")
    #     return {}
    



