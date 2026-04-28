from django.shortcuts import get_object_or_404, render

from catalog.models import GiftBox


def gift_detail(request, slug):
    gift_box = get_object_or_404(
        GiftBox.objects.prefetch_related("box_items__item", "occasions"),
        slug=slug,
        is_active=True,
    )

    return render(
        request,
        "catalog/gift_detail.html",
        {
            "gift_box": gift_box,
        },
    )
