from django.contrib import admin

from catalog.models import GiftBox, GiftBoxItem, GiftItem, Occasion


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
