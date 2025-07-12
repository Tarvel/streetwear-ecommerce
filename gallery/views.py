from django.shortcuts import render
from .models import GalleryImage

def gallery(request):
    gallery_images = GalleryImage.objects.all()
    return render(request, "gallery/gallery.html", {"gallery_images": gallery_images})