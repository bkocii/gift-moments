from django.urls import path

from orders import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart_detail, name="cart"),
    path("cart/remove/<int:index>/", views.cart_remove, name="cart_remove"),
]
