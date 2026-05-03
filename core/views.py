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
