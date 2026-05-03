from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from catalog.models import (
    BuildCategory,
    BuildOption,
    BuildYourOwnPackage,
    GiftBox,
    GiftBoxImage,
    GiftOption,
    GiftOptionGroup,
    MessageCategory,
    MessageTemplate,
)


def make_test_image(name="test.png", size=(1200, 900), color=(255, 0, 0)):
    file_obj = BytesIO()
    image = Image.new("RGB", size, color)
    image.save(file_obj, format="PNG")
    file_obj.seek(0)
    return SimpleUploadedFile(name, file_obj.read(), content_type="image/png")


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
def test_gift_detail_form_valid_post_redirects_to_cart(client):
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
            "quantity": 1,
            "flower-color": str(option.id),
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("orders:cart")


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
def test_gift_detail_form_adds_item_with_correct_total_to_cart(client):
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
            "quantity": 1,
            "flower-color": str(option.id),
        },
        follow=True,
    )

    assert response.status_code == 200
    assert b"Shopping cart" in response.content
    assert b"Premium mix" in response.content
    assert b"57.90" in response.content


@pytest.mark.django_db
def test_cart_shows_correct_total_for_multiple_selected_single_choice_options(client):
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
            "quantity": 1,
            "flower-color": str(flower_option.id),
            "wine-option": str(wine_option.id),
        },
        follow=True,
    )

    assert response.status_code == 200
    assert b"Shopping cart" in response.content
    assert b"Premium mix" in response.content
    assert b"Premium wine" in response.content
    assert b"73.00" in response.content


@pytest.mark.django_db
def test_gift_detail_form_rejects_past_delivery_date(client):
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
            "delivery_date": "2020-01-01",
            "gift_message": "Happy birthday!",
            "quantity": 1,
            "flower-color": str(option.id),
        },
    )

    assert response.status_code == 200
    assert b"Delivery date cannot be in the past." in response.content


@pytest.mark.django_db
def test_gift_detail_page_shows_gallery_images(client):
    gift_box = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses, chocolates and wine.",
        base_price="49.90",
        is_active=True,
    )
    GiftBoxImage.objects.create(
        gift_box=gift_box,
        image="gift_boxes/gallery/test1.jpg",
        alt_text="Gallery photo 1",
        is_active=True,
    )
    GiftBoxImage.objects.create(
        gift_box=gift_box,
        image="gift_boxes/gallery/test2.jpg",
        alt_text="Gallery photo 2",
        is_active=True,
    )

    response = client.get(
        reverse("catalog:gift_detail", kwargs={"slug": gift_box.slug})
    )

    assert response.status_code == 200
    assert b"Gallery photo 1" in response.content
    assert b"Gallery photo 2" in response.content


@pytest.mark.django_db
def test_gift_detail_uses_primary_gallery_image_as_main_image(client):
    gift_box = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses, chocolates and wine.",
        base_price="49.90",
        is_active=True,
        image=make_test_image("main.png"),
    )

    GiftBoxImage.objects.create(
        gift_box=gift_box,
        image=make_test_image("test1.png"),
        alt_text="Gallery photo 1",
        is_active=True,
        is_primary=False,
    )
    primary_image = GiftBoxImage.objects.create(
        gift_box=gift_box,
        image=make_test_image("test2.png"),
        alt_text="Primary gallery photo",
        is_active=True,
        is_primary=True,
    )

    response = client.get(
        reverse("catalog:gift_detail", kwargs={"slug": gift_box.slug})
    )

    assert response.status_code == 200
    assert primary_image.image.url.encode() in response.content
    assert b"Primary gallery photo" in response.content


@pytest.mark.django_db
def test_build_your_own_page_loads(client):
    response = client.get(reverse("catalog:build_your_own"))

    assert response.status_code == 200
    assert b"Build Your Own Gift" in response.content


@pytest.mark.django_db
def test_build_your_own_page_shows_packages_categories_and_messages(client):
    package = BuildYourOwnPackage.objects.create(
        name="Premium Box",
        slug="premium-box",
        base_price="20.00",
        is_active=True,
    )
    category = BuildCategory.objects.create(
        name="Flowers",
        slug="flowers",
        is_active=True,
    )
    BuildOption.objects.create(
        category=category,
        name="Red Roses",
        slug="red-roses",
        price_delta="8.00",
        is_active=True,
    )
    message_category = MessageCategory.objects.create(
        name="Birthday",
        slug="birthday",
        is_active=True,
    )
    MessageTemplate.objects.create(
        category=message_category,
        title="Warm Birthday Wish",
        text="Wishing you joy and happiness.",
        is_active=True,
    )

    response = client.get(reverse("catalog:build_your_own"))

    assert response.status_code == 200
    assert package.name.encode() in response.content
    assert category.name.encode() in response.content
    assert b"Red Roses" in response.content
    assert b"Warm Birthday Wish" in response.content


@pytest.mark.django_db
def test_build_your_own_page_valid_post_shows_summary(client):
    package = BuildYourOwnPackage.objects.create(
        name="Premium Box",
        slug="premium-box",
        base_price="20.00",
        is_active=True,
    )
    category = BuildCategory.objects.create(
        name="Flowers",
        slug="flowers",
        selection_type=BuildCategory.SelectionType.SINGLE,
        is_required=True,
        is_active=True,
    )
    option = BuildOption.objects.create(
        category=category,
        name="Red Roses",
        slug="red-roses",
        price_delta="8.00",
        is_active=True,
    )
    message_category = MessageCategory.objects.create(
        name="Birthday",
        slug="birthday",
        is_active=True,
    )
    template = MessageTemplate.objects.create(
        category=message_category,
        title="Warm Birthday Wish",
        text="Wishing you joy and happiness.",
        is_active=True,
    )

    response = client.post(
        reverse("catalog:build_your_own"),
        data={
            "package": package.id,
            f"category_{category.id}": str(option.id),
            "recipient_name": "Sara",
            "delivery_date": "2026-05-20",
            "message_mode": "template",
            "message_template": template.id,
            "custom_message": "",
        },
    )

    assert response.status_code == 200
    assert b"Premium Box" in response.content
    assert b"Sara" in response.content
    assert b"Warm Birthday Wish" in response.content


@pytest.mark.django_db
def test_build_your_own_page_requires_message_based_on_mode(client):
    package = BuildYourOwnPackage.objects.create(
        name="Premium Box",
        slug="premium-box",
        base_price="20.00",
        is_active=True,
    )

    response = client.post(
        reverse("catalog:build_your_own"),
        data={
            "package": package.id,
            "recipient_name": "Sara",
            "delivery_date": "2026-05-20",
            "message_mode": "custom",
            "custom_message": "",
            "message_template": "",
        },
    )

    assert response.status_code == 200
    assert b"Please write a message." in response.content


@pytest.mark.django_db
def test_build_your_own_page_calculates_total_for_single_select_options(client):
    package = BuildYourOwnPackage.objects.create(
        name="Premium Box",
        slug="premium-box",
        base_price="20.00",
        is_active=True,
    )
    category = BuildCategory.objects.create(
        name="Flowers",
        slug="flowers",
        selection_type=BuildCategory.SelectionType.SINGLE,
        is_required=True,
        is_active=True,
    )
    option = BuildOption.objects.create(
        category=category,
        name="Red Roses",
        slug="red-roses",
        price_delta="8.00",
        is_active=True,
    )

    response = client.post(
        reverse("catalog:build_your_own"),
        data={
            "package": package.id,
            f"category_{category.id}": str(option.id),
            "recipient_name": "Sara",
            "delivery_date": "2026-05-20",
            "message_mode": "custom",
            "custom_message": "Happy Birthday!",
            "message_template": "",
        },
    )

    assert response.status_code == 200
    assert b"Red Roses" in response.content
    assert b"28.00" in response.content


@pytest.mark.django_db
def test_build_your_own_page_calculates_total_for_multiple_select_options(client):
    package = BuildYourOwnPackage.objects.create(
        name="Premium Box",
        slug="premium-box",
        base_price="20.00",
        is_active=True,
    )
    category = BuildCategory.objects.create(
        name="Extras",
        slug="extras",
        selection_type=BuildCategory.SelectionType.MULTIPLE,
        is_required=False,
        is_active=True,
    )
    candle = BuildOption.objects.create(
        category=category,
        name="Candle",
        slug="candle",
        price_delta="6.00",
        is_active=True,
    )
    teddy = BuildOption.objects.create(
        category=category,
        name="Teddy Bear",
        slug="teddy-bear",
        price_delta="9.00",
        is_active=True,
    )

    response = client.post(
        reverse("catalog:build_your_own"),
        data={
            "package": package.id,
            f"category_{category.id}": [str(candle.id), str(teddy.id)],
            "recipient_name": "Sara",
            "delivery_date": "2026-05-20",
            "message_mode": "custom",
            "custom_message": "Enjoy your gift!",
            "message_template": "",
        },
    )

    assert response.status_code == 200
    assert b"Candle" in response.content
    assert b"Teddy Bear" in response.content
    assert b"35.00" in response.content


@pytest.mark.django_db
def test_build_your_own_page_uses_template_message_text_in_summary(client):
    package = BuildYourOwnPackage.objects.create(
        name="Premium Box",
        slug="premium-box",
        base_price="20.00",
        is_active=True,
    )
    message_category = MessageCategory.objects.create(
        name="Birthday",
        slug="birthday",
        is_active=True,
    )
    template = MessageTemplate.objects.create(
        category=message_category,
        title="Warm Birthday Wish",
        text="Wishing you joy and happiness on your special day.",
        is_active=True,
    )

    response = client.post(
        reverse("catalog:build_your_own"),
        data={
            "package": package.id,
            "recipient_name": "Sara",
            "delivery_date": "2026-05-20",
            "message_mode": "template",
            "message_template": template.id,
            "custom_message": "",
        },
    )

    assert response.status_code == 200
    assert b"Warm Birthday Wish" in response.content
    assert b"Wishing you joy and happiness on your special day." in response.content


@pytest.mark.django_db
def test_build_your_own_add_to_cart_redirects_to_cart(client):
    package = BuildYourOwnPackage.objects.create(
        name="Premium Box",
        slug="premium-box",
        base_price="20.00",
        is_active=True,
    )
    category = BuildCategory.objects.create(
        name="Flowers",
        slug="flowers",
        selection_type=BuildCategory.SelectionType.SINGLE,
        is_required=True,
        is_active=True,
    )
    option = BuildOption.objects.create(
        category=category,
        name="Red Roses",
        slug="red-roses",
        price_delta="8.00",
        is_active=True,
    )

    response = client.post(
        reverse("catalog:build_your_own"),
        data={
            "package": package.id,
            f"category_{category.id}": str(option.id),
            "recipient_name": "Sara",
            "delivery_date": "2026-05-20",
            "message_mode": "custom",
            "custom_message": "Happy Birthday!",
            "message_template": "",
            "add_to_cart": "1",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("orders:cart")

    cart_items = client.session.get("cart_items", [])

    assert len(cart_items) == 1
    assert cart_items[0]["item_type"] == "build_your_own"
    assert cart_items[0]["name"] == "Build Your Own - Premium Box"
    assert cart_items[0]["unit_price"] == "28.00"
    assert cart_items[0]["selected_options"][0]["group_name"] == "Flowers"
