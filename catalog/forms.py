from django import forms
from django.utils import timezone


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
