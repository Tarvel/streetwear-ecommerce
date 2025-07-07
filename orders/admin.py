from django.contrib import admin
from .models import Order
from payment.models import Payment

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('payment_reference', 'status', 'amount', 'created_at', 'paid_at')
    can_delete = False
    show_change_link = True

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'order_id')
    ordering = ('-created_at',)
    readonly_fields = ('order_id', 'created_at', 'updated_at')

    inlines = [PaymentInline]
