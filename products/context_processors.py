from .models import Drop
from cart.models import Cart
from orders.models import Order
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required


def drop_context(request):
    drops = Drop.objects.all().order_by("created_at")
    return {"drops": drops}

def cart_context(request):
    if request.user.is_authenticated:
        user = request.user
        cart_item_count = (
            Cart.objects.filter(user=user).count()
        )
        return {
            "cart_item_count": cart_item_count,
        }
    return {}

def order_context(request):
    if request.user.is_authenticated:
        user = request.user
        orders = Order.objects.filter(user=user)
        return {"orders": orders}
    return {}
