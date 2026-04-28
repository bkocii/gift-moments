import pytest

from catalog.models import GiftBox, GiftBoxItem, GiftItem, Occasion


@pytest.mark.django_db
def test_occasion_string_representation():
    occasion = Occasion.objects.create(name="Birthday", slug="birthday")

    assert str(occasion) == "Birthday"


@pytest.mark.django_db
def test_gift_box_string_representation():
    gift_box = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses, chocolate and wine.",
        base_price="49.90",
    )

    assert str(gift_box) == "Romantic Evening Box"


@pytest.mark.django_db
def test_gift_box_item_string_with_quantity():
    gift_box = GiftBox.objects.create(
        name="Classic Rose Box",
        slug="classic-rose-box",
        short_description="A classic flower gift.",
        base_price="35.00",
    )
    item = GiftItem.objects.create(name="Red roses")

    box_item = GiftBoxItem.objects.create(
        gift_box=gift_box,
        item=item,
        quantity="12 stems",
    )

    assert str(box_item) == "12 stems Red roses"


@pytest.mark.django_db
def test_gift_box_absolute_url():
    gift_box = GiftBox.objects.create(
        name="Premium Gift Box",
        slug="premium-gift-box",
        short_description="A premium curated gift.",
        base_price="75.00",
    )

    assert gift_box.get_absolute_url() == "/gifts/premium-gift-box/"
