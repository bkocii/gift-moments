from django.contrib import admin, messages
from django.utils.safestring import mark_safe

from orders.emails import send_order_status_email
from orders.models import Order, OrderItem


def build_selected_options_html(selected_options):
    if not selected_options:
        return "-"

    parts = []

    for item in selected_options:
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


def build_selected_options_summary(selected_options):
    if not selected_options:
        return "-"

    parts = []

    for item in selected_options:
        group_name = item.get("group_name", "Option")

        if item.get("is_multiple"):
            options = item.get("options", [])
            option_names = ", ".join(
                option.get("name", "") for option in options if option
            )
            value = option_names or "None"
        else:
            option = item.get("option")
            value = option.get("name", "None") if option else "None"

        parts.append(f"{group_name}: {value}")

    return " | ".join(parts)


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
        return mark_safe(build_selected_options_html(obj.selected_options))

    selected_options_display.short_description = "Selected options"


@admin.action(description="Mark selected orders as confirmed")
def mark_as_confirmed(modeladmin, request, queryset):
    orders = list(queryset)
    updated = queryset.update(status=Order.Status.CONFIRMED)

    for order in orders:
        order.status = Order.Status.CONFIRMED
        send_order_status_email(order)

    modeladmin.message_user(
        request,
        f"{updated} order(s) marked as confirmed.",
        level=messages.SUCCESS,
    )


@admin.action(description="Mark selected orders as preparing")
def mark_as_preparing(modeladmin, request, queryset):
    orders = list(queryset)
    updated = queryset.update(status=Order.Status.PREPARING)

    for order in orders:
        order.status = Order.Status.PREPARING
        send_order_status_email(order)

    modeladmin.message_user(
        request,
        f"{updated} order(s) marked as preparing.",
        level=messages.SUCCESS,
    )


@admin.action(description="Mark selected orders as delivered")
def mark_as_delivered(modeladmin, request, queryset):
    orders = list(queryset)
    updated = queryset.update(status=Order.Status.DELIVERED)

    for order in orders:
        order.status = Order.Status.DELIVERED
        send_order_status_email(order)

    modeladmin.message_user(
        request,
        f"{updated} order(s) marked as delivered.",
        level=messages.SUCCESS,
    )


@admin.action(description="Mark selected orders as cancelled")
def mark_as_cancelled(modeladmin, request, queryset):
    orders = list(queryset)
    updated = queryset.update(status=Order.Status.CANCELLED)

    for order in orders:
        order.status = Order.Status.CANCELLED
        send_order_status_email(order)

    modeladmin.message_user(
        request,
        f"{updated} order(s) marked as cancelled.",
        level=messages.WARNING,
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sender_name",
        "recipient_name",
        "status",
        "total_amount",
        "item_count",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "id",
        "sender_name",
        "sender_email",
        "recipient_name",
        "recipient_phone",
        "delivery_address",
    )
    readonly_fields = ("created_at", "updated_at", "total_amount")
    inlines = [OrderItemInline]
    actions = [
        mark_as_confirmed,
        mark_as_preparing,
        mark_as_delivered,
        mark_as_cancelled,
    ]
    date_hierarchy = "created_at"
    list_per_page = 25

    def item_count(self, obj):
        return obj.items.count()

    item_count.short_description = "Items"

    def save_model(self, request, obj, form, change):
        old_status = None

        if change and obj.pk:
            old_status = (
                Order.objects.filter(pk=obj.pk)
                .values_list("status", flat=True)
                .first()
            )

        super().save_model(request, obj, form, change)

        if change and old_status and old_status != obj.status:
            send_order_status_email(obj)
            self.message_user(
                request,
                f"Status email sent to {obj.sender_email}.",
                level=messages.SUCCESS,
            )


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
        "selected_options_summary",
    )
    list_filter = ("delivery_date", "order__status")
    search_fields = (
        "gift_box_name",
        "recipient_name",
        "order__id",
        "order__sender_name",
    )
    readonly_fields = ("selected_options_display",)
    list_per_page = 25

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
        return mark_safe(build_selected_options_html(obj.selected_options))

    selected_options_display.short_description = "Selected options"

    def selected_options_summary(self, obj):
        return build_selected_options_summary(obj.selected_options)

    selected_options_summary.short_description = "Options"
