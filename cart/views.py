import json
import uuid
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.utils import timezone
from .models import Cart
from payment.models import Payment
from django.urls import reverse
from payment.paystack import checkout
from orders.models import OrderItem, Order
from products.models import ProductVariant
from django.template.loader import render_to_string


@login_required(login_url="login")
def cartPage(request):
    cart_items = Cart.objects.filter(user=request.user).all()
    cart_subtotal = sum(item.total_price for item in cart_items)

    context = {
        "cart_items": cart_items,
        "cart_subtotal": cart_subtotal,
    }

    return render(request, "cart/cart.html", context)


@login_required(login_url="login")
def addToCart(request, variant_id):
    variant = ProductVariant.objects.filter(pk=variant_id).first()
    if not variant:
        messages.error(request, "Product does not exist")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity", 1))
        except ValueError:
            quantity = 1
        total_price = int(variant.price) * int(quantity)
        cart = Cart.objects.create(
            user=request.user,
            quantity=quantity,
            total_price=total_price,
            variant=variant,
        )
        messages.info(request, "Added to cart")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@login_required(login_url="login")
def updateCartShop(request, variant_id):
    try:
        variant = ProductVariant.objects.filter(pk=variant_id)
    except ProductVariant.DoesNotExist:
        messages.error(request, "Product does not exist")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
    try:
        cart = Cart.objects.filter(user=request.user, variant__id=variant_id)
    except Cart.DoesNotExist:
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

    if request.method == "POST":
        quantity = (
            request.POST.get("quantity")
            if request.POST.get("quantity") is not None
            else 1
        )
        variant_price = ProductVariant.objects.get(pk=variant_id)
        new_total_price = int(variant_price.price) * int(quantity)
        cart.update(quantity=quantity, total_price=new_total_price)
        messages.info(
            request,
            f"Updated: {quantity} {variant_price.product.name.title()}{'s' if int(quantity) > 1 else ''} in cart.",
        )
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@login_required(login_url="login")
def updateCart(request, variant_id):
    try:
        variant = ProductVariant.objects.get(pk=variant_id)
    except ProductVariant.DoesNotExist:
        return JsonResponse({"error": "Product does not exist."}, status=404)

    cart = Cart.objects.filter(user=request.user, variant__id=variant_id)

    if request.method == "POST":
        quantity = request.POST.get("quantity", 1)
        new_total_price = int(variant.price) * int(quantity)
        cart.update(quantity=quantity, total_price=new_total_price)
        msg = f"Updated: {quantity} {variant.product.name.title()}{'s' if int(quantity) > 1 else ''} in cart."

        cart_items = Cart.objects.filter(user=request.user)
        cart_subtotal = sum(item.total_price for item in cart_items)

        html = render_to_string(
            "cart/_cart_items.html",
            {
                "cart_items": cart_items,
                "cart_subtotal": cart_subtotal,
            },
            request=request,
        )

        return JsonResponse(
            {
                "html": html,
                "message": msg,
            }
        )

    return JsonResponse({"error": "Invalid request."}, status=400)


@login_required(login_url="login")
def removeCart(request, cart_id):
    try:
        cart = Cart.objects.filter(pk=cart_id).first()
    except Cart.DoesNotExist:
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

    if request.method == "POST":
        if request.POST.get("remove") == "true":
            messages.info(
                request,
                f"{cart.variant.product.name.title()} [{cart.variant.size.title()}-{cart.variant.colour.title() if cart.variant.size.title() is not None else ""}] has been removed from cart",
            )
            cart.delete()
        else:
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@login_required(login_url="login")
def checkoutPage(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        messages.info(request, "Please login to access checkout")
        return redirect("login")

    cart_items = Cart.objects.filter(user=user)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("home")

    cart_subtotal = sum(item.total_price for item in cart_items)

    if request.method == "POST":
        # generate unique ids for order and payment reference
        unique_order_id = uuid.uuid4()
        unique_reference_id = f"ord-{uuid.uuid4().hex[0:8]}"

        # Createing or get pending order
        order, created = Order.objects.get_or_create(
            user=user,
            order_id=unique_order_id,
            reference=unique_reference_id,
            status="pending",
            defaults={
                "total_amount": cart_subtotal,
                "shipping_address": user.userdetail.delivery_address,
            },
        )

        # Loop through cart items and create order items
        for cart_item in cart_items:
            OrderItem.objects.get_or_create(
                order=order,
                variant=cart_item.variant,
                defaults={
                    "quantity": cart_item.quantity,
                    "price": cart_item.variant.price,
                },
            )

        cart_items.delete()

        # convert UUID to string (cos 'Object of type UUID is not JSON serializable' lol)
        json_data = json.dumps({"order_id": str(order.order_id)})

        # Build callback URL
        payment_success_url = reverse(
            "payment-success", kwargs={"order_id": order.order_id}
        )
        callback_url = f"{request.scheme}://{request.get_host()}{payment_success_url}"

        checkout_data = {
            "email": user.email,
            "amount": int(order.total_amount * 100),  # convert to kobo
            "currency": "NGN",
            "channels": ["card", "bank_transfer", "bank", "ussd", "qr", "mobile_money"],
            "reference": str(order.reference),
            "callback_url": callback_url,
            "metadata": {
                "order_id": str(order.order_id),
                "user_id": user.id,
                "payment_reference": order.reference,
            },
            "label": f"Checkout For order: {order.order_id}",
        }

        # Call checkout logic
        status, checkout_url, payment_reference = checkout(checkout_data)

        if status:
            # if the connection to paystack is sucessful, update the order status to pending (default), cos, technically, the payment is in a pending state unless payment is scuessful
            # we will get this success status from our webhook
            order.updated_at = timezone.now()
            order.save()
            return redirect(checkout_url)

        else:
            # if theres an error, first update the order status and time the error in payment occured, then make a failed payment instance sha

            order.status = "failed"
            order.updated_at = timezone.now()
            order.save()

            payment, create = Payment.objects.get_or_create(
                order=order,
                user=user,
                defaults={
                    "amount": order.total_amount,
                },
            )

            payment.status = "failed"
            payment.paid_at = timezone.now()
            payment.save()

            messages.error(request, checkout_url)  # Shows error message
            return redirect("payment-fail", order.order_id)

    context = {
        "user": user,
        "cart_items": cart_items,
        "cart_subtotal": cart_subtotal,
    }
    return render(request, "cart/checkout.html", context)
