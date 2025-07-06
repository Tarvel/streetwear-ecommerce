from django.contrib import admin
from .forms import ProductAdminForm
from .models import (
    Product,
    Drop,
    ProductImage,
    ProductVariant,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image"]


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ["size", "colour", "price", "stock_quantity", "sku", "image"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = (
        "name",
        "drop",
        "is_available",
        "created_at",
    )
    list_filter = ("drop", "created_at")
    search_fields = ("name", "description", "base_price")
    inlines = [ProductImageInline, ProductVariantInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "slug",
                    "base_price",
                    "description",
                    "is_available",
                    "image",
                )
            },
        ),
        ("Details", {"fields": ("drop",)}),
    )
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Drop)
class DropAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    ordering = ("-created_at",)
