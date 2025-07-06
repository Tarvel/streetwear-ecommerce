from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserDetail


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "username",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class UserDetailForm(forms.ModelForm):
    class Meta:
        model = UserDetail
        fields = ["phone_number", "delivery_address"]

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        import re

        if not re.match(r"^\+\d{12,14}$", phone_number):
            raise forms.ValidationError(
                'Phone number must start with "+" followed by 12 to 14 digits (e.g., +1234567890098).'
            )
        return phone_number
