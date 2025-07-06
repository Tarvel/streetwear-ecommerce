from django.db import models
from django.utils import timezone
from accounts.models import User
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Drop(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created_at"]


class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to="products/", blank=True)
    drop = models.ForeignKey("Drop", on_delete=models.SET_NULL, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    SIZE_CHOICES = [
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
        ("XL", "Extra Large"),
        ("NA", "None"),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    size = models.CharField(max_length=2, choices=SIZE_CHOICES)
    colour = models.CharField(max_length=30, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True)
    availability = models.BooleanField(default=True)
    image = models.ImageField(upload_to="product_variants/", blank=True)

    def update_is_available(self):
        total_stock = sum(
            qty_sum.stock_quantity for qty_sum in self.product.variants.all()
        )
        self.product.is_available = total_stock > 0
        self.product.save()

    def __str__(self):
        return f"{self.product.name} - {self.size}{f' - {self.colour}' if self.colour else ''}"


@receiver(post_save, sender=ProductVariant)
@receiver(post_delete, sender=ProductVariant)
def update_product_availability(sender, instance, **kwargs):
    instance.update_is_available()


class ProductImage(models.Model):
    image = models.ImageField(upload_to="product_thumbnails/")
    product = models.ForeignKey(
        "Product",
        related_name="additional_images",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"Image for {self.product.name if self.product else 'Unassigned'}"
