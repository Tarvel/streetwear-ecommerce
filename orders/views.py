from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Order


@login_required(login_url="login")
def orderHistory(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by("-updated_at")

    context = {"orders": orders}

    return render(request, "orders/order_history.html", context)


@login_required(login_url="login")
def orderDetail(request, order_id):
    order = Order.objects.filter(order_id=order_id).first()
    time_elapsed = timezone.now() - order.created_at
    print(time_elapsed)
    show_retry_button = time_elapsed.total_seconds() > 1800
    print(show_retry_button)

    context = {
        "order": order,
        "show_retry_button": show_retry_button,
    }
    return render(request, "orders/order_detail.html", context)
