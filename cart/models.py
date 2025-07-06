from django.db import models
from accounts.models import User
from products.models import ProductVariant


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} added {self.variant} to cart"

    class Meta:
        ordering = ["-added_at"]
