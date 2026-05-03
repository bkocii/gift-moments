from django.db import models
from django.urls import reverse

from catalog.image_utils import optimize_uploaded_image


class Occasion(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="occasions/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.image:
            self.image = optimize_uploaded_image(
                self.image,
                max_width=900,
                max_height=900,
                quality=80,
            )
        super().save(*args, **kwargs)


class GiftItem(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class GiftBox(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    occasions = models.ManyToManyField(
        Occasion,
        blank=True,
        related_name="gift_boxes",
    )
    short_description = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="gift_boxes/", blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("catalog:gift_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if self.image:
            self.image = optimize_uploaded_image(
                self.image,
                max_width=1600,
                max_height=1600,
                quality=82,
            )
        super().save(*args, **kwargs)

    @property
    def primary_gallery_image(self):
        return self.gallery_images.filter(is_active=True, is_primary=True).first()

    @property
    def first_active_gallery_image(self):
        return (
            self.gallery_images.filter(is_active=True)
            .order_by("sort_order", "id")
            .first()
        )

    @property
    def display_image(self):
        if self.primary_gallery_image:
            return self.primary_gallery_image.image

        if self.image:
            return self.image

        first_gallery = self.first_active_gallery_image
        if first_gallery:
            return first_gallery.image

        return None

    @property
    def display_image_alt(self):
        if self.primary_gallery_image and self.primary_gallery_image.alt_text:
            return self.primary_gallery_image.alt_text

        return self.name


class GiftBoxItem(models.Model):
    gift_box = models.ForeignKey(
        GiftBox,
        on_delete=models.CASCADE,
        related_name="box_items",
    )
    item = models.ForeignKey(
        GiftItem,
        on_delete=models.PROTECT,
        related_name="gift_box_items",
    )
    quantity = models.CharField(
        max_length=80,
        blank=True,
        help_text="Example: 12 stems, 250g, 1 bottle",
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "item__name"]
        unique_together = ["gift_box", "item"]

    def __str__(self):
        if self.quantity:
            return f"{self.quantity} {self.item.name}"
        return self.item.name


class GiftOptionGroup(models.Model):
    class InputType(models.TextChoices):
        RADIO = "radio", "Radio"
        SELECT = "select", "Dropdown"
        CHECKBOX = "checkbox", "Checkbox"

    gift_box = models.ForeignKey(
        GiftBox,
        on_delete=models.CASCADE,
        related_name="option_groups",
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140)
    input_type = models.CharField(
        max_length=20,
        choices=InputType.choices,
        default=InputType.RADIO,
    )
    is_required = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        unique_together = ["gift_box", "slug"]

    def __str__(self):
        return f"{self.gift_box.name} - {self.name}"


class GiftOption(models.Model):
    group = models.ForeignKey(
        GiftOptionGroup,
        on_delete=models.CASCADE,
        related_name="options",
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140)
    price_delta = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="Extra price added when this option is selected.",
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        unique_together = ["group", "slug"]

    def __str__(self):
        if self.price_delta:
            return f"{self.name} (+€{self.price_delta})"
        return self.name


class GiftBoxImage(models.Model):
    gift_box = models.ForeignKey(
        GiftBox,
        on_delete=models.CASCADE,
        related_name="gallery_images",
    )
    image = models.ImageField(upload_to="gift_boxes/gallery/")
    alt_text = models.CharField(max_length=160, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.gift_box.name} image {self.pk}"

    def save(self, *args, **kwargs):
        if self.image:
            self.image = optimize_uploaded_image(
                self.image,
                max_width=1600,
                max_height=1600,
                quality=82,
            )

        super().save(*args, **kwargs)

        if self.is_primary:
            type(self).objects.filter(gift_box=self.gift_box).exclude(
                pk=self.pk
            ).update(is_primary=False)
