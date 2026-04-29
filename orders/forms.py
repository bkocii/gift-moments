from django import forms


class CheckoutForm(forms.Form):
    sender_name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    sender_email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-input"}),
    )
    sender_phone = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    recipient_name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    recipient_phone = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    delivery_address = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-textarea",
                "rows": 4,
            }
        ),
    )
    delivery_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-textarea",
                "rows": 3,
            }
        ),
    )
