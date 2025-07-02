import random
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseNotFound
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import (
    Product,
    CartItem,
    Drop,
    ContactSubmission,
    GalleryImage,
    Event,
    ProductImage,
)


def search(request):
    return render(request, "base/search.html")


def home(request):
    drops = Drop.objects.all()
    slideshow_images = list(GalleryImage.objects.all())
    random.shuffle(slideshow_images)
    newest_products = Product.objects.filter(availability=True)[0:8]
    context = {
        "drops": drops,
        "slideshow_images": slideshow_images,
        "newest_products": newest_products,
    }
    return render(request, "productapp/index.html", context)


def shop(request):
    drops = Drop.objects.all()
    sort = request.GET.get("sort") if request.GET.get("sort") is not None else ""

    if sort == "":
        products_list = Product.objects.all()
    elif sort == "low-high":
        products_list = Product.objects.all().order_by("price")
    elif sort == "high-low":
        products_list = Product.objects.all().order_by("-price")

    elif sort == "newest":
        products_list = Product.objects.all().order_by("-created_at")
    elif sort == "oldest":
        products_list = Product.objects.all().order_by("created_at")
    elif sort == "in-stock":
        products_list = Product.objects.filter(availability=True)
    elif sort == "out-of-stock":
        products_list = Product.objects.filter(availability=False)

    paginator = Paginator(products_list, 10)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    context = {
        "drops": drops,
        "products": products,
    }
    return render(request, "productapp/shop.html", context)


def shopDrops(request, drop):
    page = drop
    drops = Drop.objects.all()
    selected_drop = Drop.objects.get(name=drop)
    product_drop = Product.objects.filter(drop=selected_drop)
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
    elif sort == "in-stock":
        products_list = Product.objects.filter(
            Q(availability=True) & Q(drop=selected_drop)
        )
    elif sort == "out-of-stock":
        products_list = Product.objects.filter(
            Q(availability=False) & Q(drop=selected_drop)
        )

    paginator = Paginator(products_list, 10)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    context = {
        "drops": drops,
        "products": products,
        "page": page,
    }
    return render(request, "productapp/shop.html", context)


def product_detail(request, slug):
    drops = Drop.objects.all()
    # user_cart = CartItem.objects.get(user=request.user)
    try:
        product = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        raise Http404("Item does not exist.")
    additional_images = ProductImage.objects.filter(product=product)

    context = {
        "product": product,
        "additional_images": additional_images,
        "drops": drops,
    }

    return render(request, "productapp/product_detail.html", context)


def cartPage(request):
    drops = Drop.objects.all()
    cart_items = CartItem.objects.filter(user=request.user).all()

    context = {
        "cart_items": cart_items,
        "drops": drops,
    }

    return render(request, "productapp/cart.html", context)


def addToCart(request, pk):
    product = Product.objects.get(id=pk)
    if request.method == "POST":
        size = request.POST.get("size") if request.POST.get("size") is not None else ""
        quantity = (
            request.POST.get("quantity")
            if request.POST.get("quantity") is not None
            else 1
        )
        cart = CartItem.objects.create(
            user=request.user, product=product, quantity=int(quantity), size=size
        )
        messages.info(request, f"{product.name.title()} has been added to your cart")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


def updateCart(request, pk):
    cart = CartItem.objects.filter(product__pk=pk)
    if request.method == "POST":
        if request.POST.get("remove") == "true":
            messages.info(request, f"{cart.first().product.name.title()} has been removed from cart")
            cart.delete()
        quantity = (
            request.POST.get("quantity")
            if request.POST.get("quantity") is not None
            else 1
        )
        product = Product.objects.get(pk=pk)
        new_total_price = int(product.price) * int(quantity)
        cart.update(quantity=quantity, total_price=new_total_price)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
