from django.contrib import admin
from .models import UserDetail
from cart.models import Cart
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


# Customize UserDetail admin
@admin.register(UserDetail)
class UserDetailAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number", "delivery_address")
    search_fields = ("user__username", "phone_number", "delivery_address")
    fields = ("user", "phone_number", "delivery_address")


# Extend User admin to include UserDetail
class UserDetailInline(admin.StackedInline):
    model = UserDetail
    can_delete = False
    fields = ("phone_number", "delivery_address")

class CartlInline(admin.StackedInline):
    model = Cart
    can_delete = False
    list_display = ("product", "quantity", "size", "added_at")


class CustomUserAdmin(UserAdmin):
    inlines = [UserDetailInline]


# Re-register User model with UserDetail inline
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
