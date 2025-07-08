from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Order


@login_required(login_url="login")
def orderHistory(request):
    orders = Order.objects.all().order_by("-updated_at")

    context = {"orders": orders}

    return render(request, "orders/order_history.html", context)


@login_required(login_url="login")
def orderDetail(request, order_id):
    order = Order.objects.filter(order_id=order_id).first

    return render(request, "orders/order_detail.html", {"order": order})
