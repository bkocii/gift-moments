from django.shortcuts import render

from catalog.models import GiftBox, Occasion


def home(request):
    featured_gifts = (
        GiftBox.objects.filter(is_active=True, is_featured=True)
        .prefetch_related("box_items__item", "occasions")
        .order_by("sort_order", "name")[:6]
    )

    occasions = Occasion.objects.filter(is_active=True).order_by("sort_order", "name")

    return render(
        request,
        "core/home.html",
        {
            "featured_gifts": featured_gifts,
            "occasions": occasions,
        },
    )
