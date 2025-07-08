import uuid
from django.db import models
from products.models import ProductVariant
from django.contrib.auth.models import User


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("shipped", "Shipped"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    reference = models.CharField(default="ord-UNIQUE_ID", editable=False, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            while True:
                unique_reference = f"ord-{uuid.uuid4().hex[:8]}"
                if not Order.objects.filter(reference=unique_reference).exists():
                    self.reference = unique_reference
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.variant.product.name} [{self.variant.size if self.variant.size is not None else ''}{'-' + self.variant.colour if self.variant.colour is not None else ''}] x {self.quantity}"
