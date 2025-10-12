import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .serializers import JobStatus


class Job(BaseModel):
    uid: str
    status: JobStatus = JobStatus.PENDING
    file_path: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = None
    result: dict[str, Any] = Field(default_factory=dict)
    result_url: str = ""
    error: str = ""

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    def update(self, **kwargs) -> None:
        """Update job fields and set updated_at."""
        allowed_fields = {"status", "result", "error", "completed_at", "result_url"}
        for key, value in kwargs.items():
            if key in allowed_fields:
                object.__setattr__(self, key, value)
        self.updated_at = datetime.now()


@dataclass
class QueuedTask:
    """Represents a task queued in Redis for processing."""

    task_id: str
    uid: str
    file_path: str
    parsed_doc: dict[str, Any]  # Required first-class field for parsed document
    retries: int = 0  # Used for retry logic tracking

    def to_redis_dict(self) -> dict[str, str | int]:
        """Convert to dict for Redis storage."""
        return {
            "task_id": self.task_id,
            "uid": self.uid,
            "file_path": self.file_path,
            "parsed_doc": json.dumps(self.parsed_doc),
            "retries": self.retries,
        }

    @classmethod
    def from_redis_dict(cls, data: dict[str, str]) -> "QueuedTask":
        """Create from Redis dict data."""
        return cls(
            task_id=data["task_id"],
            uid=data["uid"],
            file_path=data["file_path"],
            parsed_doc=json.loads(data["parsed_doc"]),
            retries=int(data.get("retries", 0)),
        )
