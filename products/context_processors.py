from .models import Drop
from cart.models import Cart
from django.contrib.auth import get_user_model


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
