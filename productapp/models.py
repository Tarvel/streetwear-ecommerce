from django.db import models
from django.utils import timezone
from authapp.models import User
from django.utils.text import slugify
import uuid


class Drop(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created_at"]


class Product(models.Model):
    SIZE_CHOICES = [
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
        ("XL", "Extra Large"),
    ]
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/", blank=True)
    drop = models.ForeignKey("Drop", on_delete=models.SET_NULL, null=True, blank=True)
    sizes = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    availability = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.availability = self.stock_quantity > 0
        if not self.slug:
            base_slug_name = slugify(self.name)
            unique_slug_id = uuid.uuid4().hex[:6]
            self.slug = f"{base_slug_name}-{unique_slug_id}"
        super().save(*args, **kwargs)


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


class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="events/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-date"]


class GalleryImage(models.Model):
    url = models.ImageField(upload_to="gallery/")
    name = models.CharField(max_length=200, blank=True)
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.caption or f"Gallery Image {self.id}"

    class Meta:
        ordering = ["-created_at"]


class ContactSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contact from {self.name} at {self.submitted_at}"

    class Meta:
        ordering = ["-submitted_at"]


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=200, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} added {self.product} to cart"

    def save(self, *args, **kwargs):
        self.total_price = int(self.product.price) * self.quantity

        existing_item = (
            CartItem.objects.exclude(pk=self.pk)
            .filter(product=self.product, size=self.size)
            .first()
        )
        if existing_item:
            existing_item.quantity = int(existing_item.quantity)
            existing_item.quantity += self.quantity
            existing_item.total_price = int(existing_item.product.price) * existing_item.quantity
            existing_item.save()
            return

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-added_at"]
