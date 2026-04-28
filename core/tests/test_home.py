import pytest
from django.urls import reverse

from catalog.models import GiftBox


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
