from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .serializers import JobStatus


class Job(BaseModel):
    """Application-layer state tracker for resume processing jobs.

    Tracks user-facing job lifecycle from creation through completion.
    Stored in Redis with TTL for API responses and status queries.
    """

    uid: str
    status: JobStatus = JobStatus.PENDING
    file_path: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = None
    result: dict[str, Any] = Field(default_factory=dict)
    error: str = ""

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class JobExecution(BaseModel):
    """Internal worker queue item representing a processing attempt.

    Multiple executions may exist for one Job if retries occur.
    Not exposed to users.
    """

    execution_id: str
    job_uid: str
    file_path: str
    parsed_doc: dict[str, Any]
    attempt_number: int = 1
