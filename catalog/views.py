from django import forms
from django.contrib import messages
from django.shortcuts import get_object_or_404, render

from catalog.forms import GiftCustomizationForm
from catalog.models import GiftBox, GiftOptionGroup


def gift_detail(request, slug):
    gift_box = get_object_or_404(
        GiftBox.objects.prefetch_related(
            "box_items__item",
            "occasions",
            "option_groups__options",
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
        {"group": group, "field": form[group.slug]} for group in option_groups
    ]

    submitted_data = None

    if request.method == "POST" and form.is_valid():
        total_price = gift_box.base_price
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
                    total_price += option.price_delta

                selected_options.append(
                    {
                        "group_name": group.name,
                        "is_multiple": True,
                        "options": selected_group_options,
                    }
                )
            else:
                selected_option = (
                    group_map.get(submitted_value) if submitted_value else None
                )

                if selected_option:
                    total_price += selected_option.price_delta

                selected_options.append(
                    {
                        "group_name": group.name,
                        "is_multiple": False,
                        "option": selected_option,
                    }
                )

        submitted_data = {
            "recipient_name": form.cleaned_data["recipient_name"],
            "gift_message": form.cleaned_data["gift_message"],
            "delivery_date": form.cleaned_data["delivery_date"],
            "base_price": gift_box.base_price,
            "total_price": total_price,
            "selected_options": selected_options,
        }

        messages.success(
            request,
            "Gift customization saved successfully. Cart and checkout come next.",
        )

    return render(
        request,
        "catalog/gift_detail.html",
        {
            "gift_box": gift_box,
            "form": form,
            "option_group_fields": option_group_fields,
            "submitted_data": submitted_data,
        },
    )
