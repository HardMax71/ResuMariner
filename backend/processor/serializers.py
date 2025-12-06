import os

from django.db.models import TextChoices
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.file_types import (
    ALLOWED_EXTENSIONS,
    DANGEROUS_CHARS,
    MALWARE_PATTERNS,
    SUSPICIOUS_PATH_PATTERNS,
    validate_file_signature,
)


# https://docs.djangoproject.com/en/5.2/ref/models/fields/
class JobStatus(TextChoices):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()  # The actual file field from request.FILES

    def validate_file(self, file):
        # 1. Validate filename (cheap checks first)
        filename = file.name
        if any(char in filename for char in DANGEROUS_CHARS):
            raise ValidationError("Filename contains dangerous characters")

        if any(pattern in filename for pattern in SUSPICIOUS_PATH_PATTERNS):
            raise ValidationError("Filename contains suspicious patterns")

        # 2. Validate extension BEFORE reading file
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
            raise ValidationError(f"File extension not allowed: {file_ext}. Allowed: {allowed}")

        # 3. Validate file size BEFORE reading content (prevents DoS)
        from core.file_types import FILE_TYPE_REGISTRY

        max_size_bytes = FILE_TYPE_REGISTRY[file_ext]["max_size_mb"] * 1024 * 1024
        if file.size > max_size_bytes:
            max_mb = FILE_TYPE_REGISTRY[file_ext]["max_size_mb"]
            raise ValidationError(f"File too large. Max size for {file_ext}: {max_mb}MB")

        # 4. Validate content (only after extension/size checks pass)
        file.seek(0)
        content = file.read()

        if not validate_file_signature(file_ext, content):
            raise ValidationError(f"Invalid {file_ext} file: missing proper file signature")

        if any(pattern in content for pattern in MALWARE_PATTERNS):
            raise ValidationError("Suspicious content detected in file")

        if content.count(b"\x00") > len(content) * 0.5:
            raise ValidationError("Excessive null bytes detected")

        # Reset file pointer for later use
        file.seek(0)
        return file
