from django.contrib import admin

from catalog.models import (
    GiftBox,
    GiftBoxItem,
    GiftItem,
    GiftOption,
    GiftOptionGroup,
    Occasion,
)


@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")


@admin.register(GiftItem)
class GiftItemAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    ordering = ("name",)


class GiftBoxItemInline(admin.TabularInline):
    model = GiftBoxItem
    extra = 1
    autocomplete_fields = ("item",)


class GiftOptionInline(admin.TabularInline):
    model = GiftOption
    extra = 1
    prepopulated_fields = {"slug": ("name",)}


@admin.register(GiftOptionGroup)
class GiftOptionGroupAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "gift_box",
        "input_type",
        "is_required",
        "sort_order",
    )
    list_filter = ("input_type", "is_required", "gift_box")
    search_fields = ("name", "gift_box__name")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("gift_box",)
    inlines = [GiftOptionInline]
    ordering = ("gift_box", "sort_order", "name")


@admin.register(GiftBox)
class GiftBoxAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "base_price",
        "is_active",
        "is_featured",
        "sort_order",
        "updated_at",
    )
    list_filter = ("is_active", "is_featured", "occasions")
    search_fields = ("name", "short_description", "description")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("occasions",)
    filter_horizontal = ("occasions",)
    inlines = [GiftBoxItemInline]
    ordering = ("sort_order", "name")
