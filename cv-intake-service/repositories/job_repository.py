import json
import logging
from datetime import datetime, timedelta
from typing import Optional

import redis
from config import settings
from models.job import Job, JobUpdate, JobCreate
from redis.exceptions import RedisError
from utils.errors import RepositoryError

logger = logging.getLogger(__name__)


class JobRepository:
    """Repository for storing and retrieving job data from Redis"""

    def __init__(self):
        """Initialize Redis connection"""
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
        )
        self.prefix = settings.REDIS_JOB_PREFIX
        self.ttl = timedelta(days=settings.JOB_RETENTION_DAYS)

    def _get_key(self, job_id: str) -> str:
        """Get Redis key for a job ID"""
        return f"{self.prefix}{job_id}"

    def create(self, job_id: str, job_create: JobCreate) -> Job:
        """Create a new job in Redis"""
        try:
            job = Job(
                job_id=job_id,
                file_path=job_create.file_path,
                result={},
                result_url="",
                error="",
            )

            # Convert to dictionary and prepare for Redis
            job_dict = job.model_dump()
            job_dict["created_at"] = job_dict["created_at"].isoformat()
            job_dict["updated_at"] = job_dict["updated_at"].isoformat()

            # Serialize the result field just like in the update method
            if isinstance(job_dict.get("result"), dict):
                job_dict["result"] = json.dumps(job_dict["result"])

            # Filter out any remaining None values
            job_dict = {k: v for k, v in job_dict.items() if v is not None}
            logger.debug(f"Storing job in Redis with data: {job_dict}")

            # Store in Redis
            self.redis.hset(self._get_key(job_id), mapping=job_dict)
            self.redis.expire(self._get_key(job_id), int(self.ttl.total_seconds()))

            return job
        except Exception as e:
            logger.error(f"Redis error details: {str(e)}")
            raise RepositoryError(f"Failed to create job: {str(e)}")

    def get(self, job_id: str) -> Optional[Job]:
        """Get a job from Redis by ID"""
        try:
            job_dict = self.redis.hgetall(self._get_key(job_id))
            if not job_dict:
                return None

            # Convert strings back to proper types
            if "created_at" in job_dict:
                job_dict["created_at"] = datetime.fromisoformat(job_dict["created_at"])
            if "updated_at" in job_dict:
                job_dict["updated_at"] = datetime.fromisoformat(job_dict["updated_at"])
            if "result" in job_dict and job_dict["result"]:
                job_dict["result"] = json.loads(job_dict["result"])

            return Job(**job_dict)
        except (RedisError, ValueError) as e:
            raise RepositoryError(f"Failed to get job: {str(e)}")

    def update(self, job_id: str, job_update: JobUpdate) -> Optional[Job]:
        """Update a job in Redis"""
        try:
            job = self.get(job_id)
            if not job:
                return None

            # Update fields
            update_dict = job_update.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(job, key, value)

            # Update timestamp
            job.updated_at = datetime.now()

            # Prepare for Redis storage
            job_dict = job.model_dump()
            job_dict["created_at"] = job_dict["created_at"].isoformat()
            job_dict["updated_at"] = job_dict["updated_at"].isoformat()

            # Properly serialize all complex data structures
            for key, value in job_dict.items():
                if isinstance(value, (dict, list)):
                    try:
                        job_dict[key] = json.dumps(value, default=str)
                        logger.debug(f"Successfully serialized {key} field")
                    except Exception as e:
                        logger.error(f"Error serializing {key}: {str(e)}")
                        # Fallback - convert to string
                        job_dict[key] = str(value)

            # Filter out any None values
            job_dict = {k: v for k, v in job_dict.items() if v is not None}
            logger.debug(f"Updating job {job_id} in Redis with keys: {job_dict.keys()}")

            # Store in Redis
            self.redis.hset(self._get_key(job_id), mapping=job_dict)
            self.redis.expire(self._get_key(job_id), int(self.ttl.total_seconds()))

            return job
        except Exception as e:
            logger.error(f"Redis update error details: {str(e)}")
            import traceback

            traceback.print_exc()
            raise RepositoryError(f"Failed to update job: {str(e)}")

    def delete(self, job_id: str) -> bool:
        """Delete a job from Redis"""
        try:
            result = self.redis.delete(self._get_key(job_id))
            return result > 0
        except RedisError as e:
            raise RepositoryError(f"Failed to delete job: {str(e)}")
