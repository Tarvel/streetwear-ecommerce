from django.db import models

class GalleryImage(models.Model):
    url = models.ImageField(upload_to="gallery/")
    name = models.CharField(max_length=200, blank=True)
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.caption or f"Gallery Image {self.id}"

    class Meta:
        ordering = ["-created_at"]
