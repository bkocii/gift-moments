from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_order_confirmation_email(order):
    subject = f"Your Gift Moments order #{order.id}"

    html_message = render_to_string(
        "orders/emails/order_confirmation.html",
        {
            "order": order,
        },
    )
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=None,
        recipient_list=[order.sender_email],
        html_message=html_message,
    )
