from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from orders.cart import cart_total, clear_cart, get_cart, remove_from_cart
from orders.forms import CheckoutForm
from orders.models import Order, OrderItem


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
        messages.success(request, "Item removed from cart.")

    return redirect("orders:cart")


def checkout(request):
    cart_items = get_cart(request.session)

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect("orders:cart")

    form = CheckoutForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        order = Order.objects.create(
            sender_name=form.cleaned_data["sender_name"],
            sender_email=form.cleaned_data["sender_email"],
            sender_phone=form.cleaned_data["sender_phone"],
            recipient_name=form.cleaned_data["recipient_name"],
            recipient_phone=form.cleaned_data["recipient_phone"],
            delivery_address=form.cleaned_data["delivery_address"],
            delivery_notes=form.cleaned_data["delivery_notes"],
            total_amount=cart_total(request.session),
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                gift_box_name=item["name"],
                gift_box_slug=item["slug"],
                quantity=item["quantity"],
                recipient_name=item["recipient_name"],
                gift_message=item["gift_message"],
                delivery_date=item["delivery_date"],
                base_price=Decimal(str(item["base_price"])),
                unit_price=Decimal(str(item["unit_price"])),
                line_total=Decimal(str(item["line_total"])),
                selected_options=item["selected_options"],
            )

        clear_cart(request.session)
        messages.success(request, "Your order has been placed successfully.")
        return redirect("orders:checkout_success", order_id=order.id)

    return render(
        request,
        "orders/checkout.html",
        {
            "form": form,
            "cart_items": cart_items,
            "cart_total": cart_total(request.session),
        },
    )


def checkout_success(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        pk=order_id,
    )

    return render(
        request,
        "orders/checkout_success.html",
        {
            "order": order,
        },
    )
