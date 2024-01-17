from django.shortcuts import render, redirect, HttpResponse
from .forms import ImageForm
from .models import Uploaded_Image

# Create your views here.
def upload(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save()
            return redirect('show_image', image_id=image.id)
    else:
        form = ImageForm()

    return render(request, 'core_upload.html', {'form': form})

def show_image(request, image_id):
    try:
        image = Uploaded_Image.objects.get(id=image_id)
    except Uploaded_Image.DoesNotExist:
        return HttpResponse("Image not found", status=404)

    return render(request, 'image_result.html', {'image': image, 'form': ImageForm()})