import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

import redis
from config import settings

logger = logging.getLogger(__name__)


class RedisJobQueue:
    """Redis-based job queue manager"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )

        # Queue names
        self.job_queue = settings.REDIS_JOB_QUEUE
        self.cleanup_queue = settings.REDIS_CLEANUP_QUEUE

        # Key prefixes
        self.job_key_prefix = settings.REDIS_JOB_PREFIX
        self.task_key_prefix = "cv:task:"
        self.retry_key_prefix = "cv:retry:"

        # Test connection
        try:
            self.redis_client.ping()
            logger.info("Redis connection established")
        except redis.ConnectionError as e:
            logger.error(f"Redis connection failed: {str(e)}")
            raise

    def enqueue_job(self, job_id: str, file_path: str, priority: int = 0) -> str:
        """Enqueue a job for processing"""
        task_id = str(uuid.uuid4())

        job_data = {
            "task_id": task_id,
            "job_id": job_id,
            "file_path": file_path,
            "priority": priority,
            "enqueued_at": datetime.utcnow().isoformat(),
            "retries": 0,
            "max_retries": settings.REDIS_MAX_RETRIES,
        }

        # Store job data
        task_key = f"{self.task_key_prefix}{task_id}"
        self.redis_client.hset(task_key, mapping=job_data)
        self.redis_client.expire(task_key, settings.REDIS_JOB_TIMEOUT)

        # Add to queue based on priority
        if priority > 0:
            self.redis_client.lpush(self.job_queue, task_id)
        else:
            self.redis_client.rpush(self.job_queue, task_id)

        logger.info(f"Job {job_id} enqueued with task {task_id}")
        return task_id

    def dequeue_job(self, timeout: int = None) -> Optional[Dict[str, Any]]:
        """Dequeue a job for processing"""
        if timeout is None:
            timeout = settings.REDIS_WORKER_TIMEOUT

        try:
            # Block until job available
            result = self.redis_client.brpop(self.job_queue, timeout=timeout)
            if not result:
                return None

            _, task_id = result
            task_key = f"{self.task_key_prefix}{task_id}"

            # Get job data
            job_data = self.redis_client.hgetall(task_key)
            if not job_data:
                logger.warning(f"No job data found for task {task_id}")
                return None

            # Convert back to proper types
            job_data["priority"] = int(job_data.get("priority", 0))
            job_data["retries"] = int(job_data.get("retries", 0))
            job_data["max_retries"] = int(
                job_data.get("max_retries", settings.REDIS_MAX_RETRIES)
            )

            return job_data

        except redis.ConnectionError as e:
            logger.error(f"Redis connection error during dequeue: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error dequeuing job: {str(e)}")
            return None

    def mark_job_processing(self, task_id: str) -> bool:
        """Mark job as being processed"""
        try:
            task_key = f"{self.task_key_prefix}{task_id}"
            return self.redis_client.hset(task_key, "status", "processing") > 0
        except Exception as e:
            logger.error(f"Error marking job as processing: {str(e)}")
            return False

    def mark_job_completed(self, task_id: str, result: Dict[str, Any]) -> bool:
        """Mark job as completed with result"""
        try:
            task_key = f"{self.task_key_prefix}{task_id}"
            pipeline = self.redis_client.pipeline()
            pipeline.hset(task_key, "status", "completed")
            pipeline.hset(task_key, "completed_at", datetime.utcnow().isoformat())
            pipeline.hset(task_key, "result", json.dumps(result))
            pipeline.expire(task_key, 3600)  # Keep result for 1 hour
            pipeline.execute()
            return True
        except Exception as e:
            logger.error(f"Error marking job as completed: {str(e)}")
            return False

    def mark_job_failed(self, task_id: str, error: str, retry: bool = True) -> bool:
        """Mark job as failed and optionally retry"""
        try:
            task_key = f"{self.task_key_prefix}{task_id}"
            job_data = self.redis_client.hgetall(task_key)

            if not job_data:
                logger.warning(f"No job data found for failed task {task_id}")
                return False

            retries = int(job_data.get("retries", 0))
            max_retries = int(job_data.get("max_retries", settings.REDIS_MAX_RETRIES))

            if retry and retries < max_retries:
                # Retry the job
                retries += 1
                delay = min(
                    60 * (2**retries), 300
                )  # Exponential backoff, max 5 minutes

                pipeline = self.redis_client.pipeline()
                pipeline.hset(task_key, "retries", retries)
                pipeline.hset(task_key, "last_error", error)
                pipeline.hset(
                    task_key,
                    "retry_at",
                    (datetime.utcnow() + timedelta(seconds=delay)).isoformat(),
                )
                pipeline.execute()

                # Schedule retry
                self.redis_client.zadd(
                    f"{self.retry_key_prefix}scheduled", {task_id: time.time() + delay}
                )

                logger.info(
                    f"Job {task_id} scheduled for retry {retries}/{max_retries} in {delay} seconds"
                )
                return True
            else:
                # Mark as permanently failed
                pipeline = self.redis_client.pipeline()
                pipeline.hset(task_key, "status", "failed")
                pipeline.hset(task_key, "failed_at", datetime.utcnow().isoformat())
                pipeline.hset(task_key, "error", error)
                pipeline.expire(task_key, 86400)  # Keep failed job for 24 hours
                pipeline.execute()

                logger.error(
                    f"Job {task_id} permanently failed after {retries} retries: {error}"
                )
                return False

        except Exception as e:
            logger.error(f"Error marking job as failed: {str(e)}")
            return False

    def get_job_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and result"""
        try:
            task_key = f"{self.task_key_prefix}{task_id}"
            job_data = self.redis_client.hgetall(task_key)

            if not job_data:
                return None

            # Parse result if available
            if "result" in job_data:
                try:
                    job_data["result"] = json.loads(job_data["result"])
                except json.JSONDecodeError:
                    pass

            return job_data

        except Exception as e:
            logger.error(f"Error getting job status: {str(e)}")
            return None

    def process_retries(self) -> int:
        """Process scheduled retries"""
        try:
            current_time = time.time()
            retry_key = f"{self.retry_key_prefix}scheduled"

            # Get jobs ready for retry
            ready_jobs = self.redis_client.zrangebyscore(retry_key, 0, current_time)

            if not ready_jobs:
                return 0

            processed = 0
            for task_id in ready_jobs:
                # Re-enqueue the job
                self.redis_client.lpush(self.job_queue, task_id)
                self.redis_client.zrem(retry_key, task_id)
                processed += 1
                logger.info(f"Retrying job {task_id}")

            return processed

        except Exception as e:
            logger.error(f"Error processing retries: {str(e)}")
            return 0

    def cleanup_expired_jobs(self, max_age_hours: int = 24) -> int:
        """Clean up expired job data"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            cutoff_timestamp = cutoff_time.isoformat()

            # Find expired jobs
            pattern = f"{self.task_key_prefix}*"
            expired_jobs = []

            for key in self.redis_client.scan_iter(match=pattern):
                job_data = self.redis_client.hgetall(key)
                if job_data.get("enqueued_at", "") < cutoff_timestamp:
                    expired_jobs.append(key)

            # Delete expired jobs
            if expired_jobs:
                self.redis_client.delete(*expired_jobs)
                logger.info(f"Cleaned up {len(expired_jobs)} expired jobs")

            return len(expired_jobs)

        except Exception as e:
            logger.error(f"Error cleaning up expired jobs: {str(e)}")
            return 0

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        try:
            stats = {
                "queue_length": self.redis_client.llen(self.job_queue),
                "cleanup_queue_length": self.redis_client.llen(self.cleanup_queue),
                "scheduled_retries": self.redis_client.zcard(
                    f"{self.retry_key_prefix}scheduled"
                ),
                "active_jobs": len(
                    list(self.redis_client.scan_iter(match=f"{self.task_key_prefix}*"))
                ),
                "redis_memory_usage": self.redis_client.memory_usage("dummy")
                if hasattr(self.redis_client, "memory_usage")
                else 0,
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting queue stats: {str(e)}")
            return {}


# Global instance
redis_queue = RedisJobQueue()
