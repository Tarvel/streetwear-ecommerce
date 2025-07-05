from django.contrib import admin
from .forms import ProductAdminForm
from .models import (
    Product,
    Drop,
    Event,
    GalleryImage,
    ContactSubmission,
    ProductImage,
    ProductVariant,
    CartItem,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image"]


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ["size", "color", "price", "stock_quantity", "sku", "image"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ("name", "drop", "is_available", "created_at",)
    list_filter = ("drop", "created_at")
    search_fields = ("name", "description", "base_price")
    inlines = [ProductImageInline, ProductVariantInline]
    fieldsets = (
        (None, {"fields": ("name", "slug", "base_price", "description", "is_available", "image")}),
        ("Details", {"fields": ("drop",)}),
    )
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Drop)
class DropAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    ordering = ("-created_at",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "location", "created_at")
    list_filter = ("date",)
    search_fields = ("name", "description", "location")
    date_hierarchy = "date"
    fieldsets = (
        (None, {"fields": ("name", "date", "location", "description", "image")}),
    )


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("name", "caption", "url", "created_at")
    search_fields = ("name", "caption")
    list_filter = ("created_at",)
    fields = ("url", "name", "caption")


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "submitted_at")
    search_fields = ("name", "email", "message")
    list_filter = ("submitted_at",)
    readonly_fields = ("name", "email", "message", "submitted_at")


@admin.register(CartItem)
class CartItemsAdmin(admin.ModelAdmin):
    list_display = ("user", "variant", "quantity", "added_at")
    search_fields = ("variant__name", "user__first_name", "user__last_name")
    list_filter = ("added_at",)
    fields = ("user", "variant", "quantity")
