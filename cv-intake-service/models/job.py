from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobCreate(BaseModel):
    file_path: str


class JobUpdate(BaseModel):
    status: Optional[JobStatus] = None
    result: Optional[Dict[str, Any]] = None
    result_url: Optional[str] = None
    error: Optional[str] = None


class Job(BaseModel):
    job_id: str
    status: JobStatus = JobStatus.PENDING
    file_path: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    result: Optional[Dict[str, Any]] = None
    result_url: Optional[str] = None
    error: Optional[str] = None


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    result_url: Optional[str] = None
    error: Optional[str] = None
