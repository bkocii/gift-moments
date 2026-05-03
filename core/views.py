from django.shortcuts import render

from catalog.models import GiftBox, Occasion


def home(request):
    selected_occasion_slug = request.GET.get("occasion", "").strip()

    occasions = Occasion.objects.filter(is_active=True).order_by("sort_order", "name")

    featured_gifts = (
        GiftBox.objects.filter(is_active=True, is_featured=True)
        .prefetch_related("box_items__item", "occasions", "gallery_images")
        .order_by("sort_order", "name")
    )

    selected_occasion = None

    if selected_occasion_slug:
        selected_occasion = occasions.filter(slug=selected_occasion_slug).first()

        if selected_occasion:
            featured_gifts = featured_gifts.filter(occasions=selected_occasion)

    featured_gifts = featured_gifts[:6]

    return render(
        request,
        "core/home.html",
        {
            "featured_gifts": featured_gifts,
            "occasions": occasions,
            "selected_occasion": selected_occasion,
            "selected_occasion_slug": selected_occasion_slug,
        },
    )


@pytest.mark.django_db
def test_home_page_uses_primary_gallery_image_for_gift_card(client):
    from catalog.models import GiftBox, GiftBoxImage

    gift_box = GiftBox.objects.create(
        name="Romantic Evening Box",
        slug="romantic-evening-box",
        short_description="Roses, chocolate and wine.",
        base_price="49.90",
        is_active=True,
        is_featured=True,
        image="gift_boxes/main.jpg",
    )

    GiftBoxImage.objects.create(
        gift_box=gift_box,
        image="gift_boxes/gallery/secondary.jpg",
        is_active=True,
        is_primary=False,
    )
    GiftBoxImage.objects.create(
        gift_box=gift_box,
        image="gift_boxes/gallery/primary.jpg",
        alt_text="Primary homepage image",
        is_active=True,
        is_primary=True,
    )

    response = client.get(reverse("home"))

    assert response.status_code == 200
    assert b"gift_boxes/gallery/primary.jpg" in response.content
