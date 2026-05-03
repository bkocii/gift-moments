from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps


def optimize_uploaded_image(
    image_field_file,
    *,
    max_width: int = 1600,
    max_height: int = 1600,
    quality: int = 82,
):
    if not image_field_file:
        return image_field_file

    image_field_file.open()
    img = Image.open(image_field_file)
    img = ImageOps.exif_transpose(img)

    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    elif img.mode == "L":
        img = img.convert("RGB")

    img.thumbnail((max_width, max_height))

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)

    original_name = Path(image_field_file.name)
    new_name = original_name.with_suffix(".jpg").name

    return ContentFile(buffer.getvalue(), name=new_name)
