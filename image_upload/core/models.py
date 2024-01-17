from django.db import models

# Create your models here.
class Uploaded_Image(models.Model):
    image = models.ImageField(upload_to='images/')
    exif_data = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.image.name} - {self.id}" 
    

