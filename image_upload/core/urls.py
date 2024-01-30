from django.urls import path
from .views import upload, show_image, test_view

urlpatterns = [
    path('', upload, name='upload'),
    path('show/<int:image_id>/', show_image, name='show_image'),
    path('test_view/<int:image_id>/', test_view, name='test_view')
    
    
    
    # Add more paths for other views as needed
]