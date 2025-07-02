from django.contrib import admin
from .forms import ProductAdminForm
from .models import (
    Product,
    Drop,
    Event,
    GalleryImage,
    ContactSubmission,
    ProductImage,
    CartItem,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = (
        "name",
        "price",
        "availability",
        "stock_quantity",
        "drop",
        "created_at",
    )
    list_filter = ("availability", "drop", "created_at")
    search_fields = ("name", "description")
    list_editable = ("price", "availability", "stock_quantity")
    inlines = [ProductImageInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                    "price",
                    "image",
                    "availability",
                    "stock_quantity",
                    "sizes",
                )
            },
        ),
        ("Details", {"fields": ("drop",)}),
    )
    prepopulated_fields = {"slug": ("name",)}


# Customize Drop admin
@admin.register(Drop)
class DropAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    ordering = ("-created_at",)


# Customize Event admin
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "location", "created_at")
    list_filter = ("date",)
    search_fields = ("name", "description", "location")
    date_hierarchy = "date"
    fieldsets = (
        (None, {"fields": ("name", "date", "location", "description", "image")}),
    )


# Customize GalleryImage admin
@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("name", "caption", "url", "created_at")
    search_fields = ("name",)
    list_filter = ("created_at",)
    fields = ("url", "name", "caption")


# Customize ContactSubmission admin
@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "submitted_at")
    search_fields = ("name", "email", "message")
    list_filter = ("submitted_at",)
    readonly_fields = (
        "name",
        "email",
        "message",
        "submitted_at",
    )


# Customize GalleryImage admin
@admin.register(CartItem)
class CartItemsAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity", "size", "added_at")
    search_fields = (
        "product",
        "user",
    )
    list_filter = ("added_at",)
    fields = ("user", "product", "quantity", "size")
