from django.shortcuts import render, redirect, HttpResponse
from .forms import ImageForm
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
    
    if image.exif_data:
        image_exif_data = json.loads(image.exif_data)

    return render(request, 'image_result.html', {'image': image, 'image_exif_data': image_exif_data, 'form': ImageForm()})




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