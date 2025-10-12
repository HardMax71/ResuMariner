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
    priority: int = 0
    enqueued_at: str | None = None
    retries: int = 0
    max_retries: int = 3
    status: str | None = None
    completed_at: str | None = None
    result: dict[str, Any] | None = None
    last_error: str | None = None
    retry_at: str | None = None
    failed_at: str | None = None
    error: str | None = None

    def to_redis_dict(self) -> dict[str, str | int]:
        """Convert to dict for Redis storage."""
        data: dict[str, str | int] = {
            "task_id": self.task_id,
            "uid": self.uid,
            "file_path": self.file_path,
            "parsed_doc": json.dumps(self.parsed_doc),
            "priority": self.priority,
            "retries": self.retries,
            "max_retries": self.max_retries,
        }

        if self.enqueued_at:
            data["enqueued_at"] = self.enqueued_at
        if self.status:
            data["status"] = self.status
        if self.completed_at:
            data["completed_at"] = self.completed_at
        if self.result:
            data["result"] = json.dumps(self.result)
        if self.last_error:
            data["last_error"] = self.last_error
        if self.retry_at:
            data["retry_at"] = self.retry_at
        if self.failed_at:
            data["failed_at"] = self.failed_at
        if self.error:
            data["error"] = self.error

        return data

    @classmethod
    def from_redis_dict(cls, data: dict[str, str]) -> "QueuedTask":
        """Create from Redis dict data."""
        task = cls(
            task_id=data["task_id"],
            uid=data["uid"],
            file_path=data["file_path"],
            parsed_doc=json.loads(data["parsed_doc"]),
            priority=int(data.get("priority", 0)),
            enqueued_at=data.get("enqueued_at"),
            retries=int(data.get("retries", 0)),
            max_retries=int(data.get("max_retries", 3)),
            status=data.get("status"),
            completed_at=data.get("completed_at"),
            last_error=data.get("last_error"),
            retry_at=data.get("retry_at"),
            failed_at=data.get("failed_at"),
            error=data.get("error"),
        )

        if "result" in data:
            task.result = json.loads(data["result"])

        return task


@dataclass
class CleanupTask:
    """Represents a cleanup task in Redis."""

    uid: str
    cleanup_time: float
