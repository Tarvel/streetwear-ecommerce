from .models import Drop, CartItem
from django.contrib.auth import get_user_model


def drop_context(request):
    drops = Drop.objects.all()
    return {"drops": drops}

def cart_context(request):
    if request.user.is_authenticated:
        user = request.user
        cart_item_count = (
            CartItem.objects.filter(user=user).count()
        )
        return {
            "cart_item_count": cart_item_count,
        }
    return {}
