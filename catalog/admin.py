from django.contrib import admin
from django.utils.html import format_html

from catalog.models import (
    GiftBox,
    GiftBoxImage,
    GiftBoxItem,
    GiftItem,
    GiftOption,
    GiftOptionGroup,
    Occasion,
)


def image_preview_tag(image_field, alt_text="Preview", width=72, height=72):
    if not image_field:
        return "-"

    return format_html(
        '<img src="{}" alt="{}" style="width:{}px; height:{}px; '
        'object-fit:cover; border-radius:12px; border:1px solid #e5d6d1;" />',
        image_field.url,
        alt_text,
        width,
        height,
    )


@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    list_display = ("preview", "name", "slug", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")
    readonly_fields = ("preview_large",)

    fields = (
        "name",
        "slug",
        "description",
        "image",
        "preview_large",
        "is_active",
        "sort_order",
    )

    def preview(self, obj):
        return image_preview_tag(obj.image, obj.name, width=44, height=44)

    preview.short_description = "Image"

    def preview_large(self, obj):
        return image_preview_tag(obj.image, obj.name, width=120, height=120)

    preview_large.short_description = "Preview"


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


class GiftBoxImageInline(admin.TabularInline):
    model = GiftBoxImage
    extra = 1
    fields = (
        "preview",
        "image",
        "alt_text",
        "sort_order",
        "is_active",
        "is_primary",
    )
    readonly_fields = ("preview",)

    def preview(self, obj):
        if not obj.pk or not obj.image:
            return "-"
        return image_preview_tag(obj.image, obj.alt_text or "Gallery image")

    preview.short_description = "Preview"


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
        "preview",
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
    inlines = [GiftBoxItemInline, GiftBoxImageInline]
    ordering = ("sort_order", "name")
    readonly_fields = ("preview_large",)

    fields = (
        "name",
        "slug",
        "occasions",
        "short_description",
        "description",
        "base_price",
        "image",
        "preview_large",
        "is_active",
        "is_featured",
        "sort_order",
    )

    def preview(self, obj):
        display_image = obj.display_image
        if not display_image:
            return "-"
        return image_preview_tag(display_image, obj.display_image_alt)

    preview.short_description = "Image"

    def preview_large(self, obj):
        display_image = obj.display_image
        if not display_image:
            return "-"
        return image_preview_tag(
            display_image, obj.display_image_alt, width=140, height=140
        )

    preview_large.short_description = "Preview"
