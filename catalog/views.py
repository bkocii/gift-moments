from django import forms
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from catalog.forms import GiftCustomizationForm
from catalog.models import GiftBox, GiftOptionGroup
from orders.cart import add_to_cart


def gift_detail(request, slug):
    gift_box = get_object_or_404(
        GiftBox.objects.prefetch_related(
            "box_items__item",
            "occasions",
            "option_groups__options",
            "gallery_images",
        ),
        slug=slug,
        is_active=True,
    )

    option_groups = gift_box.option_groups.prefetch_related("options").all()

    form = GiftCustomizationForm(request.POST or None)
    group_options_map = {}

    for group in option_groups:
        active_options = list(
            group.options.filter(is_active=True).order_by("sort_order", "name")
        )
        group_options_map[group.slug] = {
            str(option.id): option for option in active_options
        }
        choices = [(str(option.id), str(option)) for option in active_options]

        if group.input_type == GiftOptionGroup.InputType.SELECT:
            form.fields[group.slug] = forms.ChoiceField(
                choices=[("", f"Choose {group.name.lower()}")] + choices,
                required=group.is_required,
                widget=forms.Select(attrs={"class": "form-select"}),
                label=group.name,
            )
        elif group.input_type == GiftOptionGroup.InputType.CHECKBOX:
            form.fields[group.slug] = forms.MultipleChoiceField(
                choices=choices,
                required=group.is_required,
                widget=forms.CheckboxSelectMultiple(),
                label=group.name,
            )
        else:
            form.fields[group.slug] = forms.ChoiceField(
                choices=choices,
                required=group.is_required,
                widget=forms.RadioSelect(),
                label=group.name,
            )

    option_group_fields = [
        {
            "group": group,
            "field": form[group.slug],
        }
        for group in option_groups
    ]

    submitted_data = None

    if request.method == "POST" and form.is_valid():
        quantity = form.cleaned_data["quantity"]
        unit_price = gift_box.base_price
        selected_options = []

        for group in option_groups:
            submitted_value = form.cleaned_data.get(group.slug)
            group_map = group_options_map.get(group.slug, {})

            if group.input_type == GiftOptionGroup.InputType.CHECKBOX:
                selected_ids = submitted_value or []
                selected_group_options = [
                    group_map[option_id]
                    for option_id in selected_ids
                    if option_id in group_map
                ]

                for option in selected_group_options:
                    unit_price += option.price_delta

                selected_options.append(
                    {
                        "group_name": group.name,
                        "is_multiple": True,
                        "options": [
                            {
                                "name": option.name,
                                "price_delta": str(option.price_delta),
                            }
                            for option in selected_group_options
                        ],
                    }
                )
            else:
                selected_option = (
                    group_map.get(submitted_value) if submitted_value else None
                )

                if selected_option:
                    unit_price += selected_option.price_delta

                selected_options.append(
                    {
                        "group_name": group.name,
                        "is_multiple": False,
                        "option": (
                            {
                                "name": selected_option.name,
                                "price_delta": str(selected_option.price_delta),
                            }
                            if selected_option
                            else None
                        ),
                    }
                )

        line_total = unit_price * quantity

        cart_item = {
            "gift_box_id": gift_box.id,
            "name": gift_box.name,
            "slug": gift_box.slug,
            "base_price": str(gift_box.base_price),
            "unit_price": str(unit_price),
            "line_total": str(line_total),
            "quantity": quantity,
            "recipient_name": form.cleaned_data["recipient_name"],
            "gift_message": form.cleaned_data["gift_message"],
            "delivery_date": form.cleaned_data["delivery_date"].isoformat(),
            "selected_options": selected_options,
        }

        add_to_cart(request.session, cart_item)

        messages.success(request, "Gift added to cart successfully.")
        return redirect("orders:cart")

    if form.is_bound and form.is_valid():
        submitted_data = {
            "recipient_name": form.cleaned_data["recipient_name"],
            "gift_message": form.cleaned_data["gift_message"],
            "delivery_date": form.cleaned_data["delivery_date"],
        }

    gallery_images = gift_box.gallery_images.filter(is_active=True).order_by(
        "sort_order", "id"
    )

    main_image_url = gift_box.image.url if gift_box.image else None
    main_image_alt = gift_box.name

    if not main_image_url and gallery_images:
        first_gallery_image = gallery_images[0]
        main_image_url = first_gallery_image.image.url
        main_image_alt = first_gallery_image.alt_text or gift_box.name

    return render(
        request,
        "catalog/gift_detail.html",
        {
            "gift_box": gift_box,
            "form": form,
            "option_group_fields": option_group_fields,
            "gallery_images": gallery_images,
            "main_image_url": main_image_url,
            "main_image_alt": main_image_alt,
        },
    )
