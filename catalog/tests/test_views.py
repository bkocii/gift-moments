import pytest
from django.urls import reverse

from catalog.models import GiftBox, GiftOption, GiftOptionGroup


@pytest.mark.django_db
def test_gift_detail_page_loads(client):
    gift_box = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses, chocolates and wine.",
        base_price="49.90",
        is_active=True,
    )

    response = client.get(
        reverse("catalog:gift_detail", kwargs={"slug": gift_box.slug})
    )

    assert response.status_code == 200
    assert b"Romantic Evening Box" in response.content
    assert b"Recipient name" in response.content


@pytest.mark.django_db
def test_gift_detail_page_renders_option_group(client):
    gift_box = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses, chocolates and wine.",
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
    GiftOption.objects.create(
        group=group,
        name="Red roses",
        slug="red-roses",
    )

    response = client.get(
        reverse("catalog:gift_detail", kwargs={"slug": gift_box.slug})
    )

    assert response.status_code == 200
    assert b"Flower color" in response.content
    assert b"Red roses" in response.content


@pytest.mark.django_db
def test_gift_detail_form_valid_post_shows_success_message(client):
    gift_box = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses, chocolates and wine.",
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
        name="Red roses",
        slug="red-roses",
    )

    response = client.post(
        reverse("catalog:gift_detail", kwargs={"slug": gift_box.slug}),
        data={
            "recipient_name": "Sara",
            "delivery_date": "2026-05-10",
            "gift_message": "Happy birthday!",
            "flower-color": str(option.id),
        },
        follow=True,
    )

    assert response.status_code == 200
    assert b"Gift customization saved successfully" in response.content
    assert b"Sara" in response.content


@pytest.mark.django_db
def test_gift_detail_form_invalid_post_shows_required_errors(client):
    gift_box = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses, chocolates and wine.",
        base_price="49.90",
        is_active=True,
    )
    GiftOptionGroup.objects.create(
        gift_box=gift_box,
        name="Flower color",
        slug="flower-color",
        input_type=GiftOptionGroup.InputType.RADIO,
        is_required=True,
    )

    response = client.post(
        reverse("catalog:gift_detail", kwargs={"slug": gift_box.slug}),
        data={
            "recipient_name": "",
            "delivery_date": "",
            "gift_message": "Hello",
        },
    )

    assert response.status_code == 200
    assert b"This field is required." in response.content


@pytest.mark.django_db
def test_gift_detail_form_shows_selected_option_name_in_preview(client):
    gift_box = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses, chocolates and wine.",
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
            "flower-color": str(option.id),
        },
        follow=True,
    )

    assert response.status_code == 200
    assert b"Premium mix" in response.content
    assert b"57.90" in response.content
    assert b"49.90" in response.content



@pytest.mark.django_db
def test_gift_detail_form_calculates_total_price_with_multiple_single_choices(client):
    gift_box = GiftBox.objects.create(
        name="Luxury Box",
        slug="luxury-box",
        short_description="Premium gift set.",
        base_price="50.00",
        is_active=True,
    )

    flower_group = GiftOptionGroup.objects.create(
        gift_box=gift_box,
        name="Flower color",
        slug="flower-color",
        input_type=GiftOptionGroup.InputType.RADIO,
        is_required=True,
    )
    flower_option = GiftOption.objects.create(
        group=flower_group,
        name="Premium mix",
        slug="premium-mix",
        price_delta="8.00",
    )

    wine_group = GiftOptionGroup.objects.create(
        gift_box=gift_box,
        name="Wine option",
        slug="wine-option",
        input_type=GiftOptionGroup.InputType.SELECT,
        is_required=True,
    )
    wine_option = GiftOption.objects.create(
        group=wine_group,
        name="Premium wine",
        slug="premium-wine",
        price_delta="15.00",
    )

    response = client.post(
        reverse("catalog:gift_detail", kwargs={"slug": gift_box.slug}),
        data={
            "recipient_name": "Ariana",
            "delivery_date": "2026-05-12",
            "gift_message": "Enjoy!",
            "flower-color": str(flower_option.id),
            "wine-option": str(wine_option.id),
        },
        follow=True,
    )

    assert response.status_code == 200
    assert b"Premium mix" in response.content
    assert b"Premium wine" in response.content
    assert b"73.00" in response.content
