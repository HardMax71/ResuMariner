import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Any

import redis
from django.conf import settings

from processor.models import CleanupTask, QueuedTask

logger = logging.getLogger(__name__)


class RedisJobQueue:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD or None,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )
        self.job_queue = settings.REDIS_JOB_QUEUE
        self.cleanup_queue = settings.REDIS_CLEANUP_QUEUE
        self.job_key_prefix = settings.REDIS_JOB_PREFIX
        self.task_key_prefix = "cv:task:"
        self.retry_key_prefix = "cv:retry:"

    def enqueue_job(self, job_id: str, file_path: str, task_data: dict | None = None, priority: int = 0) -> str:
        task_id = str(uuid.uuid4())

        task = QueuedTask(
            task_id=task_id,
            job_id=job_id,
            file_path=file_path,
            priority=priority,
            enqueued_at=datetime.now().isoformat(),
            retries=0,
            max_retries=settings.REDIS_MAX_RETRIES,
            options=task_data.get("options") if task_data else None
        )

        task_key = f"{self.task_key_prefix}{task_id}"
        redis_dict = task.to_redis_dict()
        self.redis_client.hset(task_key, mapping=redis_dict)  # type: ignore[arg-type]
        self.redis_client.expire(task_key, settings.REDIS_JOB_TIMEOUT)
        if priority > 0:
            self.redis_client.lpush(self.job_queue, task_id)
        else:
            self.redis_client.rpush(self.job_queue, task_id)
        return task_id

    def get_next_job(self, timeout: int | None = None) -> QueuedTask | None:
        if timeout is None:
            timeout = settings.REDIS_WORKER_TIMEOUT
        result = self.redis_client.brpop(self.job_queue, timeout=timeout)
        if not result:
            return None
        _, task_id = result
        task_key = f"{self.task_key_prefix}{task_id}"
        job_data = self.redis_client.hgetall(task_key)
        if not job_data:
            return None

        return QueuedTask.from_redis_dict(job_data)

    def mark_job_processing(self, task_id: str) -> bool:
        task_key = f"{self.task_key_prefix}{task_id}"
        return self.redis_client.hset(task_key, "status", "processing") > 0

    def mark_job_completed(self, task_id: str, result: dict[str, Any]) -> bool:
        task_key = f"{self.task_key_prefix}{task_id}"
        pipeline = self.redis_client.pipeline()
        pipeline.hset(task_key, "status", "completed")
        pipeline.hset(task_key, "completed_at", datetime.now().isoformat())
        pipeline.hset(task_key, "result", json.dumps(result))
        pipeline.expire(task_key, 3600)
        pipeline.execute()
        return True

    def mark_job_failed(self, task_id: str, error: str, retry: bool = True) -> bool:
        task_key = f"{self.task_key_prefix}{task_id}"
        job_data = self.redis_client.hgetall(task_key)
        if not job_data:
            return False
        retries = int(job_data.get("retries", 0))
        max_retries = int(job_data.get("max_retries", settings.REDIS_MAX_RETRIES))
        if retry and retries < max_retries:
            retries += 1
            delay = min(60 * (2 ** retries), 300)
            pipeline = self.redis_client.pipeline()
            pipeline.hset(task_key, "retries", retries)
            pipeline.hset(task_key, "last_error", error)
            pipeline.hset(task_key, "retry_at", (datetime.now() + timedelta(seconds=delay)).isoformat())
            pipeline.execute()
            self.redis_client.zadd(f"{self.retry_key_prefix}scheduled", {task_id: time.time() + delay})
            return True
        pipeline = self.redis_client.pipeline()
        pipeline.hset(task_key, "status", "failed")
        pipeline.hset(task_key, "failed_at", datetime.now().isoformat())
        pipeline.hset(task_key, "error", error)
        pipeline.expire(task_key, 86400)
        pipeline.execute()
        return False

    def get_job_status(self, task_id: str) -> QueuedTask | None:
        task_key = f"{self.task_key_prefix}{task_id}"
        job_data = self.redis_client.hgetall(task_key)
        if not job_data:
            return None
        return QueuedTask.from_redis_dict(job_data)

    def process_retries(self) -> int:
        current_time = time.time()
        retry_key = f"{self.retry_key_prefix}scheduled"
        ready_jobs = self.redis_client.zrangebyscore(retry_key, 0, current_time)
        if not ready_jobs:
            return 0
        processed = 0
        for task_id in ready_jobs:
            self.redis_client.lpush(self.job_queue, task_id)
            self.redis_client.zrem(retry_key, task_id)
            processed += 1
        return processed

    def cleanup_expired_jobs(self, max_age_hours: int = 24) -> int:
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cutoff_timestamp = cutoff_time.isoformat()
        pattern = f"{self.task_key_prefix}*"
        expired_jobs = []
        for key in self.redis_client.scan_iter(match=pattern):
            job_data = self.redis_client.hgetall(key)
            if job_data.get("enqueued_at", "") < cutoff_timestamp:
                expired_jobs.append(key)
        if expired_jobs:
            self.redis_client.delete(*expired_jobs)
        return len(expired_jobs)

    def get_queue_stats(self) -> dict[str, Any]:
        try:
            stats = {
                "queue_length": self.redis_client.llen(self.job_queue),
                "cleanup_queue_length": self.redis_client.llen(self.cleanup_queue),
                "scheduled_retries": self.redis_client.zcard(f"{self.retry_key_prefix}scheduled"),
                "active_jobs": len(list(self.redis_client.scan_iter(match=f"{self.task_key_prefix}*"))),
                "redis_memory_usage": int(self.redis_client.info("memory").get("used_memory", 0)),
            }
            return stats
        except Exception as e:
            logger.error("Error getting queue stats: %s", e)
            return {}

    def schedule_cleanup(self, cleanup_task: CleanupTask) -> None:
        """
        Schedule a cleanup task for a completed job.

        Args:
            cleanup_task: CleanupTask with job_id and cleanup_time
        """
        cleanup_data = {"job_id": cleanup_task.job_id, "cleanup_time": cleanup_task.cleanup_time}
        self.redis_client.rpush(self.cleanup_queue, json.dumps(cleanup_data))

    def get_cleanup_tasks(self) -> list[CleanupTask]:
        """
        Get all cleanup tasks from the queue.

        Returns:
            List of CleanupTask objects
        """
        tasks = []
        cleanup_items = self.redis_client.lrange(self.cleanup_queue, 0, -1)
        for item in cleanup_items:
            try:
                data = json.loads(item)
                tasks.append(CleanupTask(job_id=data["job_id"], cleanup_time=data["cleanup_time"]))
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning("Invalid cleanup task data: %s, error: %s", item, e)
        return tasks

    def remove_cleanup_task(self, job_id: str) -> bool:
        """
        Remove a cleanup task for a specific job.

        Args:
            job_id: Job identifier

        Returns:
            True if removed, False otherwise
        """
        cleanup_items = self.redis_client.lrange(self.cleanup_queue, 0, -1)
        for item in cleanup_items:
            try:
                task = json.loads(item)
                if task.get("job_id") == job_id:
                    self.redis_client.lrem(self.cleanup_queue, 1, item)
                    return True
            except json.JSONDecodeError:
                continue
        return False
