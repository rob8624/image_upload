# Generated by Django 4.2.9 on 2024-01-18 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_uploaded_image_exif_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploaded_image',
            name='exif_data',
            field=models.JSONField(default=dict),
        ),
    ]
