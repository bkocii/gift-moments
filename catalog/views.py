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

    for group in option_groups:
        active_options = group.options.filter(is_active=True).order_by(
            "sort_order", "name"
        )
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
        submitted_data = {
            "recipient_name": form.cleaned_data["recipient_name"],
            "gift_message": form.cleaned_data["gift_message"],
            "delivery_date": form.cleaned_data["delivery_date"],
            "selected_options": {},
        }

        for group in option_groups:
            submitted_data["selected_options"][group.name] = form.cleaned_data.get(
                group.slug
            )

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
