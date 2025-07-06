from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("set-theme/", views.setTheme, name='set-theme'),
    path("shops/", views.shop, name="shop"),
    path("shops/<str:drop>/", views.shopDrops, name="shop_drop"),
    path("shop/<str:slug>/", views.product_detail, name="product_detail"),
    path('about/', views.about, name='info'),
]
