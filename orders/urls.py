from django.urls import path

from orders import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart_detail, name="cart"),
    path("cart/remove/<int:index>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path(
        "checkout/success/<int:order_id>/",
        views.checkout_success,
        name="checkout_success",
    ),
]
