import json
import uuid
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator
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
from django.db import transaction, DatabaseError
from django.db.models import F


@login_required(login_url="login")
def cartPage(request):
    page = "cart"
    cart_items = Cart.objects.filter(user=request.user).all()
    cart_subtotal = sum(item.total_price for item in cart_items)

    context = {
        "page": page,
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
        messages.info(
            request,
            f"{quantity} {variant.product.name.title()}{'s' if int(quantity) > 1 else ''} added to cart.",
        )

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

    try:
        cart = Cart.objects.get(user=request.user, variant__id=variant_id)
    except Cart.DoesNotExist:
        return JsonResponse({"error": "Cart item does not exist."}, status=404)

    if request.method == "POST":
        quantity = request.POST.get("quantity", 1)
        try:
            quantity = int(quantity)
            if quantity < 1 or quantity > variant.stock_quantity:
                return JsonResponse({"error": "Invalid quantity."}, status=400)
            new_total_price = int(variant.price) * quantity
            cart.quantity = quantity
            cart.total_price = new_total_price
            cart.save()
            msg = f"Updated: {quantity} {variant.product.name.title()}{'s' if quantity > 1 else ''} in cart."
        except ValueError:
            return JsonResponse({"error": "Invalid quantity value."}, status=400)

        cart_items = Cart.objects.filter(user=request.user)
        cart_subtotal = sum(item.total_price for item in cart_items)

        context = {
            "cart_items": cart_items,
            "cart_subtotal": cart_subtotal,
            "message": msg,
        }

        if request.headers.get("HX-Request"):
            return render(request, "cart/_cart_items.html", context)
        
        return redirect("cart")

    return JsonResponse({"error": "Invalid request."}, status=400)


@login_required(login_url="login")
def removeCart(request, cart_id):
    try:
        cart = Cart.objects.get(pk=cart_id, user=request.user)
    except Cart.DoesNotExist:
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

    if request.method == "POST":
        msg = f"{cart.variant.product.name.title()} removed from cart."
        cart.delete()

        cart_items = Cart.objects.filter(user=request.user)
        cart_subtotal = sum(item.total_price for item in cart_items)

        context = {
            "cart_items": cart_items,
            "cart_subtotal": cart_subtotal,
            "message": msg,
        }

        if request.headers.get("HX-Request"):
            return render(request, "cart/_cart_items.html", context)

        messages.info(request, msg)
        return redirect("cart")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@login_required(login_url="login")
def checkoutPage(request):
    user = request.user

    # Basic Validation
    cart_items = Cart.objects.filter(user=user)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("home")

    cart_subtotal = sum(item.total_price for item in cart_items)

    if request.method == "POST":
        unique_order_id = uuid.uuid4()
        unique_reference_id = f"ord-{uuid.uuid4().hex[0:8]}"

        #define 'order' as None initially so it b can be accessed in the 'except' block if needed
        order = None

        try:
            # ATOMIC DATABASE TRANSACTION (for race conditions)
            # We reserve the stock and create the order BEFORE calling Paystack.
            with transaction.atomic():

                print("transaction lock start")

                # A. Lock the Variants (Pessimistic Locking)
                # fetch all variant IDs involved in this cart
                variant_ids = [item.variant.id for item in cart_items]

                # lock these rows.
                # .order_by('id') is CRITICAL to prevent Deadlocks if two users buy same items in different order
                locked_variants = list(
                    ProductVariant.objects.select_for_update()
                    .filter(id__in=variant_ids)
                    .order_by("id")
                )

                # Create a map for easy lookup {id: variant_instance}
                variant_map = {v.id: v for v in locked_variants}

                # B. Verify Stock and Deduct
                for item in cart_items:
                    variant = variant_map.get(item.variant.id)

                    # specific check: if product was deleted mid-transaction
                    if not variant:
                        raise ValueError(
                            f"Product {item.variant.product.name} is no longer available."
                        )

                    # Check if enough stock exists
                    if variant.stock_quantity < item.quantity:
                        raise ValueError(
                            f"Sorry, {variant.product.name} is out of stock."
                        )

                    # Deduct the stock (Reservation)
                    variant.stock_quantity -= item.quantity
                    variant.save()

                # C. Create the Order (Using 'create' since we have a unique UUID)
                print("transaction lock order created")
                order = Order.objects.create(
                    user=user,
                    order_id=unique_order_id,
                    reference=unique_reference_id,
                    status="pending",
                    total_amount=cart_subtotal,
                    shipping_address=user.userdetail.delivery_address,
                )

                # Create the Payment Instance HERE
                # We create it as PENDING. This is our log that they tried to pay.
                payment = Payment.objects.create(
                    order=order,
                    user=user,
                    payment_reference=unique_reference_id, # Link it by the reference
                    amount=order.total_amount,
                    status="pending",
                )

                # D. Create Order Items
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        variant=cart_item.variant,
                        quantity=cart_item.quantity,
                        price=cart_item.variant.price,
                    )

                # E. Clear the User's Cart
                cart_items.delete()
                print("transaction lock cart deleted")

        except ValueError as e:
            # This catches our custom stock errors
            messages.error(request, str(e))
            return redirect("cart")  # Redirect back to cart page

        except DatabaseError:
            # This catches database locks/timeouts
            print("transaction lock in place, diff user buying")
            messages.error(
                request, "The system is busy processing other orders. Please try again."
            )
            return redirect("cart")


        # STEP 2: NETWORK REQUEST (Outside Transaction)
        # The stock is now reserved. Now we talk to Paystack.

        payment_success_url = reverse(
            "payment-success", kwargs={"order_id": order.order_id}
        )
        callback_url = f"{request.scheme}://{request.get_host()}{payment_success_url}"

        checkout_data = {
            "email": user.email or user.username,
            "amount": int(order.total_amount * 100),
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

        # Call Paystack
        status, checkout_url, payment_reference = checkout(checkout_data)

        if status:
            return redirect(checkout_url)

        else:
            # FAILURE: Paystack refused to connect (or API error)
            # COMPENSATION TRANSACTION
            # We must restore the stock we deducted in Step 1

            with transaction.atomic():
                order.status = "failed"
                order.save()
                
                # update the existing payment to failed
                payment.status = "failed"
                payment.save()

                # Restore Stock
                # We iterate over the order items we just created
                for item in order.items.all():
                    # Use F expression for atomic update on restoration
                    item.variant.stock_quantity = F("stock_quantity") + item.quantity
                    item.variant.save()


            messages.error(request, "Could not initialize payment provider.")
            return redirect("payment-fail", order.order_id)

    context = {
        "user": user,
        "cart_items": cart_items,
        "cart_subtotal": cart_subtotal,
    }
    return render(request, "cart/checkout.html", context)
