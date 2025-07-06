from django.contrib import admin
from .models import GalleryImage


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("name", "caption", "url", "created_at")
    search_fields = ("name", "caption")
    list_filter = ("created_at",)
    fields = ("url", "name", "caption")
