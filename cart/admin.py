from django.contrib import admin
from .models import Cart


# Register your models here.
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "variant", "quantity", "added_at")
    search_fields = ("variant__name", "user__first_name", "user__last_name")
    list_filter = ("added_at",)
    fields = ("user", "variant", "quantity")
