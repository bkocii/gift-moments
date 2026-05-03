from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from catalog.models import (
    BuildCategory,
    BuildOption,
    BuildYourOwnPackage,
    GiftBox,
    GiftBoxImage,
    GiftBoxItem,
    GiftItem,
    GiftOption,
    GiftOptionGroup,
    MessageCategory,
    MessageTemplate,
    Occasion,
    PackageCategoryRule,
)


def make_test_image(name="test.png", size=(2400, 1800), color=(255, 0, 0)):
    file_obj = BytesIO()
    image = Image.new("RGB", size, color)
    image.save(file_obj, format="PNG")
    file_obj.seek(0)
    return SimpleUploadedFile(name, file_obj.read(), content_type="image/png")


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
        image=make_test_image("gallery.png"),
    )

    assert str(image) == f"Romantic Evening Box image {image.pk}"


@pytest.mark.django_db
def test_occasion_can_store_image():
    occasion = Occasion.objects.create(
        name="Birthday",
        slug="birthday",
        image=make_test_image("birthday.png"),
    )

    assert occasion.image.name.startswith("occasions/")
    assert occasion.image.name.endswith(".jpg")


@pytest.mark.django_db
def test_only_one_primary_gallery_image_per_gift_box():
    gift_box = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses and wine.",
        base_price="49.90",
    )

    first_image = GiftBoxImage.objects.create(
        gift_box=gift_box,
        image=make_test_image("test1.png"),
        is_primary=True,
    )
    second_image = GiftBoxImage.objects.create(
        gift_box=gift_box,
        image=make_test_image("test2.png"),
        is_primary=True,
    )

    first_image.refresh_from_db()
    second_image.refresh_from_db()

    assert first_image.is_primary is False
    assert second_image.is_primary is True


@pytest.mark.django_db
def test_gift_box_image_is_converted_to_jpg():
    gift_box = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses and wine.",
        base_price="49.90",
        image=make_test_image(),
    )

    assert gift_box.image.name.endswith(".jpg")


@pytest.mark.django_db
def test_occasion_image_is_converted_to_jpg():
    occasion = Occasion.objects.create(
        name="Birthday",
        slug="birthday",
        image=make_test_image("occasion.png"),
    )

    assert occasion.image.name.endswith(".jpg")


@pytest.mark.django_db
def test_build_your_own_package_string_representation():
    package = BuildYourOwnPackage.objects.create(
        name="Premium Box",
        slug="premium-box",
        base_price="20.00",
    )

    assert str(package) == "Premium Box"


@pytest.mark.django_db
def test_build_category_string_representation():
    category = BuildCategory.objects.create(
        name="Flowers",
        slug="flowers",
        selection_type=BuildCategory.SelectionType.SINGLE,
    )

    assert str(category) == "Flowers"


@pytest.mark.django_db
def test_build_option_string_representation():
    category = BuildCategory.objects.create(
        name="Flowers",
        slug="flowers",
    )
    option = BuildOption.objects.create(
        category=category,
        name="Red Roses",
        slug="red-roses",
        price_delta="8.00",
    )

    assert str(option) == "Red Roses (+€8.00)"


@pytest.mark.django_db
def test_package_category_rule_string_representation():
    package = BuildYourOwnPackage.objects.create(
        name="Premium Box",
        slug="premium-box",
        base_price="20.00",
    )
    category = BuildCategory.objects.create(
        name="Flowers",
        slug="flowers",
    )
    rule = PackageCategoryRule.objects.create(
        package=package,
        category=category,
    )

    assert str(rule) == "Premium Box - Flowers"


@pytest.mark.django_db
def test_message_template_string_representation():
    category = MessageCategory.objects.create(
        name="Birthday",
        slug="birthday",
    )
    template = MessageTemplate.objects.create(
        category=category,
        title="Warm Birthday Wish",
        text="Wishing you joy and happiness on your special day.",
    )

    assert str(template) == "Birthday - Warm Birthday Wish"
