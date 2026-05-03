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


@pytest.mark.django_db
def test_adding_identical_customized_gift_merges_cart_item(client):
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

    post_data = {
        "recipient_name": "Sara",
        "delivery_date": "2026-05-10",
        "gift_message": "Happy birthday!",
        "quantity": 1,
        "flower-color": str(option.id),
    }

    client.post(
        reverse("catalog:gift_detail", kwargs={"slug": gift_box.slug}), data=post_data
    )
    client.post(
        reverse("catalog:gift_detail", kwargs={"slug": gift_box.slug}), data=post_data
    )

    session = client.session
    cart_items = session.get("cart_items", [])

    assert len(cart_items) == 1
    assert cart_items[0]["quantity"] == 2
    assert cart_items[0]["line_total"] == "115.80"


@pytest.mark.django_db
def test_updating_cart_quantity_recalculates_line_total(client):
    session = client.session
    session["cart_items"] = [
        {
            "gift_box_id": 1,
            "name": "Romantic Evening Box",
            "slug": "romantic-evening-box",
            "base_price": "49.90",
            "unit_price": "57.90",
            "line_total": "57.90",
            "quantity": 1,
            "recipient_name": "Sara",
            "gift_message": "Happy birthday!",
            "delivery_date": "2026-05-10",
            "selected_options": [],
        }
    ]
    session.save()

    response = client.post(
        reverse("orders:cart_update", kwargs={"index": 0}),
        data={"quantity": 3},
    )

    assert response.status_code == 302
    assert response.url == reverse("orders:cart")

    updated_session = client.session
    cart_items = updated_session.get("cart_items", [])

    assert cart_items[0]["quantity"] == 3
    assert cart_items[0]["line_total"] == "173.70"


@pytest.mark.django_db
def test_updating_cart_quantity_to_zero_removes_item(client):
    session = client.session
    session["cart_items"] = [
        {
            "gift_box_id": 1,
            "name": "Romantic Evening Box",
            "slug": "romantic-evening-box",
            "base_price": "49.90",
            "unit_price": "57.90",
            "line_total": "57.90",
            "quantity": 1,
            "recipient_name": "Sara",
            "gift_message": "Happy birthday!",
            "delivery_date": "2026-05-10",
            "selected_options": [],
        }
    ]
    session.save()

    response = client.post(
        reverse("orders:cart_update", kwargs={"index": 0}),
        data={"quantity": 0},
    )

    assert response.status_code == 302
    assert response.url == reverse("orders:cart")

    updated_session = client.session
    assert updated_session.get("cart_items", []) == []


@pytest.mark.django_db
def test_cart_page_shows_build_your_own_item(client):
    session = client.session
    session["cart_items"] = [
        {
            "item_type": "build_your_own",
            "package_id": 1,
            "name": "Build Your Own - Premium Box",
            "slug": "premium-box",
            "base_price": "20.00",
            "unit_price": "28.00",
            "line_total": "28.00",
            "quantity": 1,
            "recipient_name": "Sara",
            "gift_message": "Happy Birthday!",
            "delivery_date": "2026-05-20",
            "selected_options": [
                {
                    "group_name": "Flowers",
                    "is_multiple": False,
                    "option": {
                        "name": "Red Roses",
                        "price_delta": "8.00",
                    },
                }
            ],
            "message_mode": "custom",
            "message_template_title": "",
        }
    ]
    session.save()

    response = client.get(reverse("orders:cart"))

    assert response.status_code == 200
    assert b"Build Your Own - Premium Box" in response.content
    assert b"Custom built gift" in response.content
    assert b"Red Roses" in response.content
    assert b"28.00" in response.content
