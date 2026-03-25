"""Local file storage service with MIME validation and size limits."""
import os
import uuid
from pathlib import Path

import aiofiles

from app.core.exceptions import AppException
from app.core.config import get_settings

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class LocalFileStorage:
    """Stores uploaded files to a local directory. Easily replaceable
    with an S3 or Cloudinary implementation in production."""

    def __init__(self) -> None:
        settings = get_settings()
        self.base_dir = Path(settings.upload_dir)

    async def save(
        self,
        file_bytes: bytes,
        content_type: str,
        subdirectory: str,
        original_filename: str,
    ) -> str:
        """Validate and save a file. Returns the relative URL path."""
        # 1. Validate MIME type
        if content_type not in ALLOWED_MIME_TYPES:
            raise AppException(
                code="INVALID_FILE_TYPE",
                message=f"File type '{content_type}' is not allowed. Use JPEG, PNG, or WebP.",
                status_code=400,
            )

        # 2. Validate size
        if len(file_bytes) > MAX_FILE_SIZE:
            raise AppException(
                code="FILE_TOO_LARGE",
                message="File exceeds the maximum size of 5 MB.",
                status_code=400,
            )

        # 3. Generate safe filename
        ext = self._get_extension(content_type)
        safe_name = f"{uuid.uuid4().hex}{ext}"
        target_dir = self.base_dir / subdirectory
        target_dir.mkdir(parents=True, exist_ok=True)

        file_path = target_dir / safe_name

        # 4. Write asynchronously
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_bytes)

        # Return relative URL path
        return f"/uploads/{subdirectory}/{safe_name}"

    @staticmethod
    def _get_extension(content_type: str) -> str:
        ext_map = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
        }
        return ext_map.get(content_type, ".bin")
