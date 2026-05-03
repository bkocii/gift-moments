from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from catalog.models import GiftBox, GiftBoxImage, Occasion


def make_test_image(name="test.png", size=(1200, 900), color=(255, 0, 0)):
    file_obj = BytesIO()
    image = Image.new("RGB", size, color)
    image.save(file_obj, format="PNG")
    file_obj.seek(0)
    return SimpleUploadedFile(name, file_obj.read(), content_type="image/png")


@pytest.mark.django_db
def test_home_page_loads(client):
    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert b"Gift Moments" in response.content


@pytest.mark.django_db
def test_home_page_shows_featured_active_gift_boxes(client):
    GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses, chocolate and wine.",
        base_price="49.90",
        is_active=True,
        is_featured=True,
    )

    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert b"Romantic Evening Box" in response.content


@pytest.mark.django_db
def test_home_page_does_not_show_inactive_gift_boxes(client):
    GiftBox.objects.create(
        name="Hidden Gift Box",
        slug="hidden-gift-box",
        short_description="This should not appear.",
        base_price="99.90",
        is_active=False,
        is_featured=True,
    )

    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert b"Hidden Gift Box" not in response.content


@pytest.mark.django_db
def test_home_page_does_not_show_unfeatured_gift_boxes(client):
    GiftBox.objects.create(
        name="Normal Gift Box",
        slug="normal-gift-box",
        short_description="This should not appear on homepage.",
        base_price="29.90",
        is_active=True,
        is_featured=False,
    )

    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert b"Normal Gift Box" not in response.content


@pytest.mark.django_db
def test_home_page_filters_gift_boxes_by_occasion(client):
    romantic = Occasion.objects.create(name="Romantic", slug="romantic")
    birthday = Occasion.objects.create(name="Birthday", slug="birthday")

    romantic_gift = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses, chocolate and wine.",
        base_price="49.90",
        is_active=True,
        is_featured=True,
    )
    romantic_gift.occasions.add(romantic)

    birthday_gift = GiftBox.objects.create(
        name="Birthday Sweet Box",
        slug="birthday-sweet-box",
        short_description="Flowers and sweets.",
        base_price="39.90",
        is_active=True,
        is_featured=True,
    )
    birthday_gift.occasions.add(birthday)

    response = client.get(reverse("home"), {"occasion": "romantic"})

    assert response.status_code == 200
    assert b"Romantic Evening Box" in response.content
    assert b"Birthday Sweet Box" not in response.content


@pytest.mark.django_db
def test_home_page_invalid_occasion_slug_falls_back_to_all_gifts(client):
    GiftBox.objects.create(
        name="Visible Gift Box",
        slug="visible-gift-box",
        short_description="Should still appear.",
        base_price="29.90",
        is_active=True,
        is_featured=True,
    )

    response = client.get(reverse("home"), {"occasion": "does-not-exist"})

    assert response.status_code == 200
    assert b"Visible Gift Box" in response.content


@pytest.mark.django_db
def test_home_page_shows_occasion_image_when_present(client):
    Occasion.objects.create(
        name="Birthday",
        slug="birthday",
        image=make_test_image("birthday.png"),
        is_active=True,
    )

    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert b"occasions/" in response.content


@pytest.mark.django_db
def test_home_page_uses_primary_gallery_image_for_gift_card(client):
    gift_box = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses, chocolate and wine.",
        base_price="49.90",
        is_active=True,
        is_featured=True,
        image=make_test_image("main.png"),
    )

    GiftBoxImage.objects.create(
        gift_box=gift_box,
        image=make_test_image("secondary.png"),
        is_active=True,
        is_primary=False,
    )
    primary_image = GiftBoxImage.objects.create(
        gift_box=gift_box,
        image=make_test_image("primary.png"),
        alt_text="Primary homepage image",
        is_active=True,
        is_primary=True,
    )

    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert primary_image.image.url.encode() in response.content
