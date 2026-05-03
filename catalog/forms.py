from django import forms
from django.utils import timezone

from catalog.models import BuildCategory, BuildYourOwnPackage, MessageTemplate


class GiftCustomizationForm(forms.Form):
    recipient_name = forms.CharField(
        max_length=120,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Recipient name",
                "class": "form-input",
            }
        ),
    )
    gift_message = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Write your gift message...",
                "rows": 5,
                "class": "form-textarea",
            }
        ),
    )
    delivery_date = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-input",
            }
        ),
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        required=True,
        widget=forms.NumberInput(
            attrs={
                "class": "form-input",
            }
        ),
    )

    def clean_delivery_date(self):
        delivery_date = self.cleaned_data["delivery_date"]

        if delivery_date < timezone.localdate():
            raise forms.ValidationError("Delivery date cannot be in the past.")

        return delivery_date


class BuildYourOwnForm(forms.Form):
    package = forms.ModelChoiceField(
        queryset=BuildYourOwnPackage.objects.filter(is_active=True).order_by(
            "sort_order", "name"
        ),
        empty_label="Choose a package",
        widget=forms.RadioSelect,
    )
    recipient_name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Recipient name",
            }
        ),
    )
    delivery_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-input",
            }
        ),
    )
    message_mode = forms.ChoiceField(
        choices=[
            ("custom", "Write my own"),
            ("template", "Choose a suggested message"),
        ],
        initial="custom",
        widget=forms.RadioSelect,
    )
    custom_message = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-textarea",
                "rows": 5,
                "placeholder": "Write your message here...",
            }
        ),
    )
    message_template = forms.ModelChoiceField(
        queryset=MessageTemplate.objects.filter(is_active=True)
        .select_related("category")
        .order_by("category__sort_order", "sort_order", "title"),
        required=False,
        empty_label="Choose a message template",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, categories=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.categories = categories or []

        for category in self.categories:
            active_options = category.options.filter(is_active=True).order_by(
                "sort_order", "name"
            )
            choices = [(str(option.id), str(option)) for option in active_options]

            field_name = f"category_{category.id}"

            if category.selection_type == BuildCategory.SelectionType.MULTIPLE:
                self.fields[field_name] = forms.MultipleChoiceField(
                    choices=choices,
                    required=category.is_required,
                    widget=forms.CheckboxSelectMultiple,
                    label=category.name,
                )
            else:
                self.fields[field_name] = forms.ChoiceField(
                    choices=choices,
                    required=category.is_required,
                    widget=forms.RadioSelect,
                    label=category.name,
                )

    def clean_delivery_date(self):
        delivery_date = self.cleaned_data["delivery_date"]

        if delivery_date < timezone.localdate():
            raise forms.ValidationError("Delivery date cannot be in the past.")

        return delivery_date

    def clean(self):
        cleaned_data = super().clean()

        message_mode = cleaned_data.get("message_mode")
        custom_message = (cleaned_data.get("custom_message") or "").strip()
        message_template = cleaned_data.get("message_template")

        if message_mode == "custom" and not custom_message:
            self.add_error("custom_message", "Please write a message.")
        elif message_mode == "template" and not message_template:
            self.add_error("message_template", "Please choose a message template.")

        return cleaned_data
