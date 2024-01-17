from django.urls import path
from .views import upload, show_image

urlpatterns = [
    path('', upload, name='upload'),
    path('show/<int:image_id>/', show_image, name='show_image')
    
    
    # Add more paths for other views as needed
]