from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment_reference', 'order', 'user', 'status', 'amount', 'created_at', 'paid_at')
    list_filter = ('status', 'created_at')
    search_fields = ('payment_reference', 'user__username', 'order__order_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'paid_at')
