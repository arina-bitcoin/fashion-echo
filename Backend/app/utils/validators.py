from fastapi import UploadFile
from Backend.app.core.exceptions import ValidationException

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_image_file(file: UploadFile):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValidationException("Only JPEG, PNG and WebP images are allowed")

    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_FILE_SIZE:
        max_mb = MAX_FILE_SIZE // 1024 // 1024
        raise ValidationException(f"File size exceeds {max_mb}MB")
