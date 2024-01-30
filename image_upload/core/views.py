from django.shortcuts import render, redirect, HttpResponse
from .forms import ImageForm, ResultsForm
from .models import Uploaded_Image

from PIL import Image as PILImage
from PIL.ExifTags import TAGS
 
import json 

# Create your views here.
def upload(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save()
            exif_data = extract_exif_data(image.image.path)
            print(exif_data)
            image.exif_data = exif_data
            image.save()
            return redirect('show_image', image_id=image.id)
    else:
        form = ImageForm()

    return render(request, 'core_upload.html', {'form': form})



def show_image(request, image_id):
    try:
        image = Uploaded_Image.objects.get(id=image_id)
    except Uploaded_Image.DoesNotExist:
        return HttpResponse("Image not found", status=404)
    image_exif_data = {}
    if image.exif_data:
        image_exif_data = json.loads(image.exif_data)

    return render(request, 'image_result.html', {'image': image, 'image_exif_data': image_exif_data, 'form': ImageForm()})


def test_view(request, image_id):
    #gets an instance of uploaded_image
    image = Uploaded_Image.objects.get(id=image_id)
    #creates a empty dict to hold the exif
    image_exif_data = {}
    #get data from the exif_data table (extracted in previous view) and convert to JSON. 
    if image.exif_data:
        image_exif_data = json.loads(image.exif_data)
    #creat a instance of ResultsForm (forms.py) and prefill with image_exif_data
    form = ResultsForm(request.POST or None, initial={'data': image_exif_data})
    #if the sumbit but is clicked logic passes through this....
    #we check for the HTMX and HTMX trigger request.....
    if request.htmx and request.htmx.trigger == "edit-data":
        #we get a copy of the request.POST (QueryDict)...we have to use a copt are original from DJANGO is immutable
        data = request.POST.copy()
        #we remove teh CSRF token from QueryDict
        csrf_token = data.pop('csrfmiddlewaretoken', None)
        #we change the image_exif_data dict (second line) to the new data
        image_exif_data = data
        #we then convert this to JSON
        image.exif_data = json.dumps(image_exif_data)
        #we save to DB
        image.save()
        #logice to save to actual image still to do!
        exif_bytes = image.exif_data.encode('utf-8')
        with PILImage.open(image.image.path) as img:
            filename = image.image.path
            img.save(filename, "JPEG", exif=exif_bytes)
       


        
        return HttpResponse("data saved")
    return render(request, 'test_template.html', {'form': form, 'image': image})








def extract_exif_data(image_path):
    try:
        with PILImage.open(image_path) as img:
            exif_data = {}
            for key in img._getexif():
                if key in TAGS and img._getexif()[key]:
                    exif_data[TAGS[key]] = img._getexif()[key]
            exif_data_json = json.dumps(exif_data, default=str)
            
            return exif_data_json
    except Exception as e:
        print(f"Error extracting EXIF data from {image_path}: {e}")
        return {}
    



