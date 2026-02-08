from typing import List
from fastapi import HTTPException, UploadFile

MAX_IMAGE_SIZE_BYTES: int = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]


def validate_image_files(image_files: List[UploadFile]) -> None:
    """Validate uploaded image files.

    Args:
        image_files: List of uploaded files.

    Raises:
        HTTPException: If any file is invalid.
    """
    for image_file in image_files:
        if image_file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail="Unsupported image type")
        image_file.file.seek(0, 2)
        file_size: int = image_file.file.tell()
        image_file.file.seek(0)
        if file_size > MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="Image size exceeds limit")
