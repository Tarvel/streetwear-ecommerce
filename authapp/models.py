from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+\d{12,14}$',
                message='Phone number must start with "+" followed by 12 to 14 digits (e.g., +1234567890098).'
            )
        ]
    )
    address = models.CharField(max_length=255)

    def __str__(self):
        return f"Details for {self.user.username}"
