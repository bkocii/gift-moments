from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PREPARING = "preparing", "Preparing"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    sender_name = models.CharField(max_length=120)
    sender_email = models.EmailField()
    sender_phone = models.CharField(max_length=50, blank=True)

    recipient_name = models.CharField(max_length=120)
    recipient_phone = models.CharField(max_length=50, blank=True)

    delivery_address = models.TextField()
    delivery_notes = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} - {self.sender_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    gift_box_name = models.CharField(max_length=160)
    gift_box_slug = models.SlugField(max_length=180)

    quantity = models.PositiveIntegerField(default=1)

    recipient_name = models.CharField(max_length=120)
    gift_message = models.TextField(blank=True)
    delivery_date = models.DateField()

    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    selected_options = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.gift_box_name} x {self.quantity}"

    def selected_options_summary_list(self):
        if not self.selected_options:
            return []

        rows = []

        for item in self.selected_options:
            group_name = item.get("group_name", "Option")

            if item.get("is_multiple"):
                options = item.get("options", [])
                values = []

                for option in options:
                    name = option.get("name", "")
                    delta = option.get("price_delta", "0.00")

                    if delta not in ("0", "0.00", "", None):
                        prefix = "+" if not str(delta).startswith("-") else ""
                        values.append(f"{name} ({prefix}€{delta})")
                    else:
                        values.append(name)

                value = ", ".join(values) if values else "None"
            else:
                option = item.get("option")
                if option:
                    name = option.get("name", "")
                    delta = option.get("price_delta", "0.00")

                    if delta not in ("0", "0.00", "", None):
                        prefix = "+" if not str(delta).startswith("-") else ""
                        value = f"{name} ({prefix}€{delta})"
                    else:
                        value = name
                else:
                    value = "None"

            rows.append(
                {
                    "group_name": group_name,
                    "value": value,
                }
            )

        return rows

    def formatted_selected_options(self):
        if not self.selected_options:
            return "-"

        parts = []

        for item in self.selected_options:
            group_name = item.get("group_name", "Option")

            if item.get("is_multiple"):
                options = item.get("options", [])
                if options:
                    option_lines = []
                    for option in options:
                        name = option.get("name", "")
                        delta = option.get("price_delta", "0.00")
                        if delta not in ("0", "0.00", "", None):
                            prefix = "+" if not str(delta).startswith("-") else ""
                            option_lines.append(f"{name} ({prefix}€{delta})")
                        else:
                            option_lines.append(name)
                    value = "<br>".join(option_lines)
                else:
                    value = "None"
            else:
                option = item.get("option")
                if option:
                    name = option.get("name", "")
                    delta = option.get("price_delta", "0.00")
                    if delta not in ("0", "0.00", "", None):
                        prefix = "+" if not str(delta).startswith("-") else ""
                        value = f"{name} ({prefix}€{delta})"
                    else:
                        value = name
                else:
                    value = "None"

            parts.append(f"<strong>{group_name}:</strong> {value}")

        return "<br><br>".join(parts)
