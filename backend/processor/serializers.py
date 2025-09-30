import os
from datetime import datetime
from enum import StrEnum

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.file_types import (
    ALLOWED_EXTENSIONS,
    DANGEROUS_CHARS,
    MALWARE_PATTERNS,
    SUSPICIOUS_PATH_PATTERNS,
    validate_file_signature,
)

"""
> python -c "from processor.serializers import JobStatus; print('JobStatus values:', list(JobStatus))"
returns:  [<JobStatus.PENDING: 'pending'>, <JobStatus.PROCESSING: 'processing'>,
     <JobStatus.COMPLETED: 'completed'>, <JobStatus.FAILED: 'failed'>]

Weird things with <> (cause of __repr__) = bad!

> python -c "from processor.serializers import JobStatus; print('JobStatus values:', [s.value for s in JobStatus])"
returns: JobStatus values: ['pending', 'processing', 'completed', 'failed']

`s.value for s in ..` in every place = code smell = bad!

TODO: Maybe some 3rd better option available?

* inheriting from StrEnum with `__repr__: self.value` is also code smell tbh
"""


class JobStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()  # The actual file field from request.FILES

    def validate_file(self, file):
        # Validate filename
        filename = file.name
        if any(char in filename for char in DANGEROUS_CHARS):
            raise ValidationError("Filename contains dangerous characters")

        if any(pattern in filename for pattern in SUSPICIOUS_PATH_PATTERNS):
            raise ValidationError("Filename contains suspicious patterns")

        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise ValidationError(f"File extension not allowed: {file_ext}")

        # Read and validate content
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


class JobCreateSerializer(serializers.Serializer):
    file_path = serializers.CharField(min_length=1)

    def validate_file_path_not_empty(self, value):
        if not value or not value.strip():
            raise ValidationError("File path cannot be empty")
        return value.strip()


class JobUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[s.value for s in JobStatus], required=False)
    result = serializers.JSONField(required=False)
    result_url = serializers.URLField(required=False, allow_blank=True)
    error = serializers.CharField(required=False, allow_blank=True)
    completed_at = serializers.DateTimeField(required=False)


class JobSerializer(serializers.Serializer):
    job_id = serializers.CharField()
    status = serializers.ChoiceField(choices=[s.value for s in JobStatus], default=JobStatus.PENDING)
    file_path = serializers.CharField()
    created_at = serializers.DateTimeField(default=datetime.now)
    updated_at = serializers.DateTimeField(default=datetime.now)
    result = serializers.JSONField(required=False, allow_null=True)
    result_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    error = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    user_id = serializers.CharField(required=False, allow_null=True)
    completed_at = serializers.DateTimeField(required=False, allow_null=True)
    error_message = serializers.CharField(required=False, allow_null=True)


class JobResponseSerializer(serializers.Serializer):
    job_id = serializers.CharField()
    status = serializers.ChoiceField(choices=[s.value for s in JobStatus])
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    result_url = serializers.URLField(required=False, allow_null=True)
    error = serializers.CharField(required=False, allow_null=True)
