from django import forms


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
