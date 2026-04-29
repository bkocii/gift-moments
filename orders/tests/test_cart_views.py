import pytest
from django.urls import reverse

from catalog.models import GiftBox, GiftOption, GiftOptionGroup


@pytest.mark.django_db
def test_valid_gift_customization_post_redirects_to_cart(client):
    gift_box = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses and wine.",
        base_price="49.90",
        is_active=True,
    )
    group = GiftOptionGroup.objects.create(
        gift_box=gift_box,
        name="Flower color",
        slug="flower-color",
        input_type=GiftOptionGroup.InputType.RADIO,
        is_required=True,
    )
    option = GiftOption.objects.create(
        group=group,
        name="Premium mix",
        slug="premium-mix",
        price_delta="8.00",
    )

    response = client.post(
        reverse("catalog:gift_detail", kwargs={"slug": gift_box.slug}),
        data={
            "recipient_name": "Sara",
            "delivery_date": "2026-05-10",
            "gift_message": "Happy birthday!",
            "quantity": 2,
            "flower-color": str(option.id),
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("orders:cart")


@pytest.mark.django_db
def test_cart_page_shows_added_item(client):
    gift_box = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses and wine.",
        base_price="49.90",
        is_active=True,
    )
    group = GiftOptionGroup.objects.create(
        gift_box=gift_box,
        name="Flower color",
        slug="flower-color",
        input_type=GiftOptionGroup.InputType.RADIO,
        is_required=True,
    )
    option = GiftOption.objects.create(
        group=group,
        name="Premium mix",
        slug="premium-mix",
        price_delta="8.00",
    )

    client.post(
        reverse("catalog:gift_detail", kwargs={"slug": gift_box.slug}),
        data={
            "recipient_name": "Sara",
            "delivery_date": "2026-05-10",
            "gift_message": "Happy birthday!",
            "quantity": 2,
            "flower-color": str(option.id),
        },
    )

    response = client.get(reverse("orders:cart"))

    assert response.status_code == 200
    assert b"Romantic Evening Box" in response.content
    assert b"Sara" in response.content
    assert b"115.80" in response.content


@pytest.mark.django_db
def test_cart_remove_deletes_item(client):
    gift_box = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses and wine.",
        base_price="49.90",
        is_active=True,
    )
    group = GiftOptionGroup.objects.create(
        gift_box=gift_box,
        name="Flower color",
        slug="flower-color",
        input_type=GiftOptionGroup.InputType.RADIO,
        is_required=True,
    )
    option = GiftOption.objects.create(
        group=group,
        name="Premium mix",
        slug="premium-mix",
        price_delta="8.00",
    )

    client.post(
        reverse("catalog:gift_detail", kwargs={"slug": gift_box.slug}),
        data={
            "recipient_name": "Sara",
            "delivery_date": "2026-05-10",
            "gift_message": "Happy birthday!",
            "quantity": 1,
            "flower-color": str(option.id),
        },
    )

    response = client.post(reverse("orders:cart_remove", kwargs={"index": 0}))

    assert response.status_code == 302
    assert response.url == reverse("orders:cart")

    cart_response = client.get(reverse("orders:cart"))
    assert b"Romantic Evening Box" not in cart_response.content
