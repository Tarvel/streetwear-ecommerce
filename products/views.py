import random
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from cart.models import Cart
from .models import (
    Product,
    Drop,
)


def home(request):
    slideshow_images = list(Product.objects.all())
    random.shuffle(slideshow_images)
    newest_products = Product.objects.filter(is_available=True).order_by("-created_at")[
        0:6
    ]
    context = {
        "slideshow_images": slideshow_images,
        "newest_products": newest_products,
    }
    return render(request, "products/index.html", context)


def shop(request):
    sort = request.GET.get("sort", "")
    products_list = Product.objects.all().order_by("-created_at")
    q = request.GET.get("q")
    if q:
        products_list = Product.objects.filter(name__icontains=q).order_by(
            "-created_at"
        )

    if sort == "low-high":
        products_list = products_list.order_by("base_price")
    elif sort == "high-low":
        products_list = products_list.order_by("-base_price")
    elif sort == "newest":
        products_list = products_list.order_by("-created_at")
    elif sort == "oldest":
        products_list = products_list.order_by("created_at")

    paginator = Paginator(products_list, 8)
    page_number = request.GET.get("page")
    products_ = paginator.get_page(page_number)

    context = {
        "products": products_,
    }

    if (
        request.headers.get("HX-Request")
        or request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"
    ):
        # Return just the grid HTML
        return render(request, "products/_product_grid.html", context)

    return render(request, "products/shop.html", context)


def shopDrops(request, drop):
    page = drop
    selected_drop = Drop.objects.get(name=drop)
    product_drop = Product.objects.filter(drop=selected_drop).order_by("-created_at")
    sort = request.GET.get("sort") if request.GET.get("sort") is not None else ""

    if sort == "":
        products_list = product_drop
    elif sort == "low-high":
        products_list = product_drop.order_by("price")
    elif sort == "high-low":
        products_list = product_drop.order_by("-price")

    elif sort == "newest":
        products_list = product_drop.order_by("-created_at")
    elif sort == "oldest":
        products_list = product_drop.order_by("created_at")

    paginator = Paginator(products_list, 8)
    page_number = request.GET.get("page")
    products_ = paginator.get_page(page_number)

    context = {
        "products": products_,
        "page": page,
    }
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(request, "products/_product_grid.html", context)

    return render(request, "products/shop.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related("variants", "additional_images"), slug=slug
    )
    variants = product.variants.all()
    selected_variant = None
    variant_id_str = request.GET.get("variant")

    if variant_id_str:
        selected_variant = next(
            (v for v in variants if str(v.id) == variant_id_str), None
        )
        if not selected_variant:
            messages.warning(request, "The selected option is no longer available.")
            return redirect("product_detail", slug=slug)

    if not selected_variant and variants:
        selected_variant = variants[0]

    cart_item = None
    if request.user.is_authenticated and selected_variant:
        cart_item = Cart.objects.filter(
            user=request.user, variant=selected_variant
        ).first()

    context = {
        "product": product,
        "variants": variants,
        "selected_variant": selected_variant,
        "cart": cart_item,
    }
    return render(request, "products/product_detail.html", context)


@csrf_exempt
def setTheme(request):
    if request.method == "POST":
        data = json.loads(request.body)
        theme = data.get("theme")
        if theme in ["dark", "light"]:
            request.session["theme"] = theme
            return JsonResponse({"status": "success"})
        return JsonResponse({"status": "invalid theme"}, status=400)
    return JsonResponse({"error": "invalid request"}, status=405)


def about(request):
    return render(request, "products/about.html")
