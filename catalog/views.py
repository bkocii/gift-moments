from decimal import Decimal

from django import forms
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from catalog.forms import BuildYourOwnForm, GiftCustomizationForm
from catalog.models import (
    BuildCategory,
    BuildYourOwnPackage,
    GiftBox,
    GiftOptionGroup,
    MessageCategory,
)
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

    primary_gallery_image = gallery_images.filter(is_primary=True).first()

    main_image_url = None
    main_image_alt = gift_box.name

    if primary_gallery_image:
        main_image_url = primary_gallery_image.image.url
        main_image_alt = primary_gallery_image.alt_text or gift_box.name
    elif gift_box.image:
        main_image_url = gift_box.image.url
        main_image_alt = gift_box.name
    elif gallery_images:
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
            "primary_gallery_image": primary_gallery_image,
            "submitted_data": submitted_data,
        },
    )


def build_your_own(request):
    packages = BuildYourOwnPackage.objects.filter(is_active=True).order_by(
        "sort_order", "name"
    )

    categories = (
        BuildCategory.objects.filter(is_active=True)
        .prefetch_related("options")
        .order_by("sort_order", "name")
    )

    message_categories = (
        MessageCategory.objects.filter(is_active=True)
        .prefetch_related("templates")
        .order_by("sort_order", "name")
    )

    form = BuildYourOwnForm(request.POST or None, categories=categories)

    category_fields = [
        {
            "category": category,
            "field": form[f"category_{category.id}"],
        }
        for category in categories
    ]

    submitted_data = None

    if request.method == "POST" and form.is_valid():
        package = form.cleaned_data["package"]
        total_price = Decimal(str(package.base_price))
        selected_categories = []
        cart_selected_categories = []

        for category in categories:
            field_name = f"category_{category.id}"
            selected_value = form.cleaned_data.get(field_name)

            if category.selection_type == BuildCategory.SelectionType.MULTIPLE:
                selected_ids = selected_value or []
                selected_options = list(
                    category.options.filter(
                        is_active=True,
                        id__in=selected_ids,
                    ).order_by("sort_order", "name")
                )

                for option in selected_options:
                    total_price += option.price_delta

                selected_categories.append(
                    {
                        "category_name": category.name,
                        "is_multiple": True,
                        "options": selected_options,
                    }
                )
                cart_selected_categories.append(
                    {
                        "group_name": category.name,
                        "is_multiple": True,
                        "options": [
                            {
                                "name": option.name,
                                "price_delta": str(option.price_delta),
                            }
                            for option in selected_options
                        ],
                    }
                )
            else:
                selected_option = None
                if selected_value:
                    selected_option = category.options.filter(
                        is_active=True,
                        id=selected_value,
                    ).first()

                if selected_option:
                    total_price += selected_option.price_delta

                selected_categories.append(
                    {
                        "category_name": category.name,
                        "is_multiple": False,
                        "option": selected_option,
                    }
                )
                cart_selected_categories.append(
                    {
                        "group_name": category.name,
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

        final_message = ""
        message_template = form.cleaned_data.get("message_template")

        if form.cleaned_data["message_mode"] == "template":
            final_message = message_template.text if message_template else ""
        else:
            final_message = form.cleaned_data["custom_message"]

        if "add_to_cart" in request.POST:
            cart_item = {
                "item_type": "build_your_own",
                "package_id": package.id,
                "name": f"Build Your Own - {package.name}",
                "slug": package.slug,
                "base_price": str(package.base_price),
                "unit_price": str(total_price),
                "line_total": str(total_price),
                "quantity": 1,
                "recipient_name": form.cleaned_data["recipient_name"],
                "gift_message": final_message,
                "delivery_date": form.cleaned_data["delivery_date"].isoformat(),
                "selected_options": cart_selected_categories,
                "message_mode": form.cleaned_data["message_mode"],
                "message_template_title": (
                    message_template.title if message_template else ""
                ),
            }

            add_to_cart(request.session, cart_item)
            messages.success(request, "Custom gift added to cart successfully.")
            return redirect("orders:cart")

        submitted_data = {
            "package": package,
            "recipient_name": form.cleaned_data["recipient_name"],
            "delivery_date": form.cleaned_data["delivery_date"],
            "message_mode": form.cleaned_data["message_mode"],
            "message_template": message_template,
            "final_message": final_message,
            "selected_categories": selected_categories,
            "total_price": total_price,
        }

    return render(
        request,
        "catalog/build_your_own.html",
        {
            "packages": packages,
            "categories": categories,
            "message_categories": message_categories,
            "form": form,
            "category_fields": category_fields,
            "submitted_data": submitted_data,
        },
    )
