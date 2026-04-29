import pytest
from django.urls import reverse

from orders.models import Order, OrderItem


@pytest.mark.django_db
def test_checkout_redirects_to_cart_when_empty(client):
    response = client.get(reverse("orders:checkout"))

    assert response.status_code == 302
    assert response.url == reverse("orders:cart")


@pytest.mark.django_db
def test_checkout_creates_order_and_items_and_clears_cart(client):
    session = client.session
    session["cart_items"] = [
        {
            "gift_box_id": 1,
            "name": "Romantic Evening Box",
            "slug": "romantic-evening-box",
            "base_price": "49.90",
            "unit_price": "57.90",
            "line_total": "115.80",
            "quantity": 2,
            "recipient_name": "Sara",
            "gift_message": "Happy birthday!",
            "delivery_date": "2026-05-10",
            "selected_options": [
                {
                    "group_name": "Flower color",
                    "is_multiple": False,
                    "option": {
                        "name": "Premium mix",
                        "price_delta": "8.00",
                    },
                }
            ],
        }
    ]
    session.save()

    response = client.post(
        reverse("orders:checkout"),
        data={
            "sender_name": "Burim",
            "sender_email": "burim@example.com",
            "sender_phone": "12345",
            "recipient_name": "Sara",
            "recipient_phone": "67890",
            "delivery_address": "Main street 10",
            "delivery_notes": "Call on arrival",
        },
    )

    assert response.status_code == 302

    assert Order.objects.count() == 1
    assert OrderItem.objects.count() == 1

    order = Order.objects.first()
    item = OrderItem.objects.first()

    assert order.sender_name == "Burim"
    assert order.recipient_name == "Sara"
    assert str(order.total_amount) == "115.80"

    assert item.gift_box_name == "Romantic Evening Box"
    assert item.quantity == 2
    assert str(item.line_total) == "115.80"

    session = client.session
    assert session.get("cart_items") == []


@pytest.mark.django_db
def test_checkout_success_page_loads(client):
    order = Order.objects.create(
        sender_name="Burim",
        sender_email="burim@example.com",
        recipient_name="Sara",
        delivery_address="Main street 10",
        total_amount="115.80",
    )

    response = client.get(
        reverse("orders:checkout_success", kwargs={"order_id": order.id})
    )

    assert response.status_code == 200
    assert b"Order placed successfully" in response.content
    assert b"115.80" in response.content


@pytest.mark.django_db
def test_checkout_success_returns_404_for_missing_order(client):
    response = client.get(
        reverse("orders:checkout_success", kwargs={"order_id": 99999})
    )

    assert response.status_code == 404
