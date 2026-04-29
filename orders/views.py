from django.shortcuts import redirect, render

from orders.cart import cart_total, get_cart, remove_from_cart


def cart_detail(request):
    cart_items = get_cart(request.session)

    return render(
        request,
        "orders/cart.html",
        {
            "cart_items": cart_items,
            "cart_total": cart_total(request.session),
        },
    )


def cart_remove(request, index):
    if request.method == "POST":
        remove_from_cart(request.session, index)

    return redirect("orders:cart")
