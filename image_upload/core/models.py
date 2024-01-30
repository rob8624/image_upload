from django.db import models

import os

# Create your models here.
class Uploaded_Image(models.Model):
    image = models.ImageField(upload_to='images/')
    exif_data = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.image.name} - {self.id}" 
    
    
    #basename os method extracts the last component of a path
    @property
    def filename(self):
        return os.path.basename(self.image.name)


