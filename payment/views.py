from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from orders.models import Order
from django.contrib import messages


@login_required(login_url="login")
def paymentSuccessful(request, order_id):
    user = request.user
    order = Order.objects.get(order_id=order_id)

    context = {
        "order": order,
        "user": user,
    }
    return render(request, "payment/payment_successful.html", context)


@login_required(login_url="login")
def paymentFailed(request, order_id):
    return render(request, "payment/payment_failed.html")
