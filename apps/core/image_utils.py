import io
import os
from PIL import Image
from django.core.files.base import ContentFile

def convert_image_to_webp(image_field, max_width=1200, max_height=1200, quality=85):
    """
    Converts uploaded image to WebP format, resizes if larger than max dimensions,
    and returns a Django ContentFile with .webp extension.
    """
    if not image_field or not hasattr(image_field, 'file'):
        return None

    try:
        img = Image.open(image_field)
        
        # Convert RGBA / P to RGB if saving as webp (webp supports RGBA too, but ensure proper mode)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            img_format = 'WEBP'
        else:
            img = img.convert('RGB')
            img_format = 'WEBP'

        # Thumbnail to keep aspect ratio within max bounds
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        output = io.BytesIO()
        img.save(output, format=img_format, quality=quality, method=6)
        output.seek(0)

        # Build clean filename
        base_name = os.path.splitext(os.path.basename(image_field.name))[0]
        webp_name = f"{base_name}.webp"

        return ContentFile(output.read(), name=webp_name)
    except Exception as e:
        # If conversion fails for any reason, keep original
        return None
