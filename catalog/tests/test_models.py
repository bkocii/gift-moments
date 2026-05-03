import pytest

from catalog.models import (
    GiftBox,
    GiftBoxImage,
    GiftBoxItem,
    GiftItem,
    GiftOption,
    GiftOptionGroup,
    Occasion,
)


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


@pytest.mark.django_db
def test_gift_option_group_string_representation():
    gift_box = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses and wine.",
        base_price="49.90",
    )

    group = GiftOptionGroup.objects.create(
        gift_box=gift_box,
        name="Flower color",
        slug="flower-color",
        input_type=GiftOptionGroup.InputType.RADIO,
        is_required=True,
    )

    assert str(group) == "Romantic Evening Box - Flower color"


@pytest.mark.django_db
def test_gift_option_string_without_price_delta():
    gift_box = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses and wine.",
        base_price="49.90",
    )
    group = GiftOptionGroup.objects.create(
        gift_box=gift_box,
        name="Flower color",
        slug="flower-color",
    )

    option = GiftOption.objects.create(
        group=group,
        name="Red roses",
        slug="red-roses",
    )

    assert str(option) == "Red roses"


@pytest.mark.django_db
def test_gift_option_string_with_price_delta():
    gift_box = GiftBox.objects.create(
        name="Luxury Gift Box",
        slug="luxury-gift-box",
        short_description="Premium curated gift.",
        base_price="89.90",
    )
    group = GiftOptionGroup.objects.create(
        gift_box=gift_box,
        name="Wine option",
        slug="wine-option",
    )

    option = GiftOption.objects.create(
        group=group,
        name="Premium red wine",
        slug="premium-red-wine",
        price_delta="12.50",
    )

    assert str(option) == "Premium red wine (+€12.50)"


@pytest.mark.django_db
def test_gift_box_image_string_representation():
    gift_box = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses and wine.",
        base_price="49.90",
    )

    image = GiftBoxImage.objects.create(
        gift_box=gift_box,
        image="gift_boxes/gallery/test.jpg",
    )

    assert str(image) == f"Romantic Evening Box image {image.pk}"


@pytest.mark.django_db
def test_occasion_can_store_image():
    occasion = Occasion.objects.create(
        name="Birthday",
        slug="birthday",
        image="occasions/birthday.jpg",
    )

    assert occasion.image.name == "occasions/birthday.jpg"
