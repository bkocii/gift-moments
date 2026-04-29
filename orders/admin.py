from django.contrib import admin
from django.utils.safestring import mark_safe

from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False

    fields = (
        "gift_box_name",
        "quantity",
        "recipient_name",
        "delivery_date",
        "unit_price",
        "line_total",
        "selected_options_display",
    )

    readonly_fields = (
        "gift_box_name",
        "quantity",
        "recipient_name",
        "delivery_date",
        "unit_price",
        "line_total",
        "selected_options_display",
    )

    def selected_options_display(self, obj):
        if not obj.selected_options:
            return "-"

        parts = []

        for item in obj.selected_options:
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

        return mark_safe(obj.formatted_selected_options())

    selected_options_display.short_description = "Selected options"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sender_name",
        "recipient_name",
        "status",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "sender_name",
        "sender_email",
        "recipient_name",
        "recipient_phone",
    )
    readonly_fields = ("created_at", "updated_at", "total_amount")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "gift_box_name",
        "quantity",
        "recipient_name",
        "delivery_date",
        "line_total",
    )
    list_filter = ("delivery_date",)
    search_fields = ("gift_box_name", "recipient_name")
    readonly_fields = ("selected_options_display",)

    fields = (
        "order",
        "gift_box_name",
        "gift_box_slug",
        "quantity",
        "recipient_name",
        "gift_message",
        "delivery_date",
        "base_price",
        "unit_price",
        "line_total",
        "selected_options_display",
    )

    def selected_options_display(self, obj):
        if not obj.selected_options:
            return "-"

        parts = []

        for item in obj.selected_options:
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

        return mark_safe("<br><br>".join(parts))

    selected_options_display.short_description = "Selected options"
