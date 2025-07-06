from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "location", "latitude", "longitude", "created_at")
    list_filter = ("date",)
    search_fields = ("name", "description", "location")
    date_hierarchy = "date"
    fieldsets = (
        (None, {"fields": ("name", "slug", "date", "location", "latitude", "longitude", "description", "image")}),
    )

    prepopulated_fields = {"slug": ("name",)}
