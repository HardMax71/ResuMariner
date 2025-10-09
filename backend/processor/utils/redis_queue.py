import asyncio
import json
import logging
import time
import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timedelta
from typing import Any

import redis.asyncio as aioredis
from asgiref.sync import async_to_sync
from django.conf import settings

from processor.models import CleanupTask, QueuedTask

logger = logging.getLogger(__name__)


class RedisJobQueue:
    def __init__(self):
        self.redis = None  # Will be initialized when needed
        self.job_stream = "cv:jobs:stream"
        self.consumer_group = "workers"
        self.consumer_name = f"worker-{uuid.uuid4().hex[:8]}"
        self.cleanup_queue = settings.REDIS_CLEANUP_QUEUE
        self.job_key_prefix = settings.REDIS_JOB_PREFIX
        self.task_key_prefix = "cv:task:"
        self.retry_set = "cv:retry:scheduled"
        self.pubsub = None

    async def enqueue_job(self, uid: str, file_path: str, task_data: dict | None = None, priority: int = 0) -> str:
        redis_client = await self.get_redis()
        task_id = str(uuid.uuid4())

        task = QueuedTask(
            task_id=task_id,
            uid=uid,
            file_path=file_path,
            priority=priority,
            enqueued_at=datetime.now().isoformat(),
            retries=0,
            max_retries=settings.REDIS_MAX_RETRIES,
            options=task_data.get("options") if task_data else None,
        )

        task_key = f"{self.task_key_prefix}{task_id}"
        redis_dict = task.to_redis_dict()

        pipeline = redis_client.pipeline()
        pipeline.hset(task_key, mapping=redis_dict)  # type: ignore[arg-type]
        pipeline.expire(task_key, settings.REDIS_JOB_TIMEOUT)

        # Add to stream for instant delivery
        stream_data = {"task_id": task_id, "uid": uid, "priority": str(priority), "timestamp": str(time.time())}
        pipeline.xadd(self.job_stream, stream_data)

        # Publish event for instant notification
        pipeline.publish("cv:jobs:new", task_id)

        await pipeline.execute()
        return task_id

    def enqueue_job_sync(self, uid: str, file_path: str, task_data: dict | None = None, priority: int = 0) -> str:
        """Sync wrapper for enqueue_job for use in sync Django views"""
        return async_to_sync(self.enqueue_job)(uid, file_path, task_data, priority)

    async def get_redis(self) -> aioredis.Redis:
        if not self.redis:
            self.redis = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                password=settings.REDIS_PASSWORD or None,
                decode_responses=True,
            )
            # Create consumer group if it doesn't exist
            try:
                await self.redis.xgroup_create(self.job_stream, self.consumer_group, id="0", mkstream=True)
            except aioredis.ResponseError as e:
                if "BUSYGROUP" not in str(e):
                    raise
        return self.redis

    async def consume_jobs(self) -> AsyncIterator[QueuedTask]:
        redis_client = await self.get_redis()

        while True:
            try:
                # Block forever until a job arrives - no timeout needed
                messages = await redis_client.xreadgroup(
                    self.consumer_group,
                    self.consumer_name,
                    {self.job_stream: ">"},
                    count=1,
                    block=0,  # Block indefinitely until message arrives
                )

                if not messages:
                    continue

                for _stream, stream_messages in messages:
                    for msg_id, data in stream_messages:
                        task_id = data.get("task_id")
                        if task_id:
                            task_key = f"{self.task_key_prefix}{task_id}"
                            job_data = await redis_client.hgetall(task_key)
                            if job_data:
                                # Acknowledge message
                                await redis_client.xack(self.job_stream, self.consumer_group, msg_id)
                                yield QueuedTask.from_redis_dict(job_data)

            except aioredis.ConnectionError:
                logger.error("Redis connection lost, reconnecting...")
                await asyncio.sleep(1)
                self.redis = None  # Force reconnection

    async def mark_job_processing(self, task_id: str, uid: str) -> bool:
        redis_client = await self.get_redis()
        task_key = f"{self.task_key_prefix}{task_id}"

        pipeline = redis_client.pipeline()
        pipeline.hset(task_key, "status", "processing")
        pipeline.publish(
            f"cv:job:{uid}:status", json.dumps({"status": "processing", "timestamp": datetime.now().isoformat()})
        )
        results = await pipeline.execute()
        return bool(results[0] > 0)

    async def mark_job_completed(self, task_id: str, uid: str, result: dict[str, Any]) -> bool:
        redis_client = await self.get_redis()
        task_key = f"{self.task_key_prefix}{task_id}"

        pipeline = redis_client.pipeline()
        pipeline.hset(task_key, "status", "completed")
        pipeline.hset(task_key, "completed_at", datetime.now().isoformat())
        pipeline.hset(task_key, "result", json.dumps(result))
        pipeline.expire(task_key, 3600)

        # Publish completion event for real-time updates
        pipeline.publish(
            f"cv:job:{uid}:completed",
            json.dumps({"status": "completed", "uid": uid, "timestamp": datetime.now().isoformat()}),
        )

        await pipeline.execute()
        return True

    async def mark_job_failed(self, task_id: str, uid: str, error: str, retry: bool = True) -> bool:
        redis_client = await self.get_redis()
        task_key = f"{self.task_key_prefix}{task_id}"
        job_data = await redis_client.hgetall(task_key)
        if not job_data:
            return False
        retries = int(job_data.get("retries", 0))
        max_retries = int(job_data.get("max_retries", settings.REDIS_MAX_RETRIES))
        if retry and retries < max_retries:
            retries += 1
            delay = min(60 * (2**retries), 300)

            pipeline = redis_client.pipeline()
            pipeline.hset(task_key, "retries", retries)
            pipeline.hset(task_key, "last_error", error)
            pipeline.hset(task_key, "retry_at", (datetime.now() + timedelta(seconds=delay)).isoformat())

            # Schedule retry using sorted set
            pipeline.zadd(self.retry_set, {task_id: time.time() + delay})

            # Set expiry key for notification
            pipeline.setex(f"cv:retry:{task_id}", delay, uid)

            await pipeline.execute()
            return True

        pipeline = redis_client.pipeline()
        pipeline.hset(task_key, "status", "failed")
        pipeline.hset(task_key, "failed_at", datetime.now().isoformat())
        pipeline.hset(task_key, "error", error)
        pipeline.expire(task_key, 86400)

        # Publish failure event
        pipeline.publish(
            f"cv:job:{uid}:failed",
            json.dumps({"status": "failed", "error": error, "timestamp": datetime.now().isoformat()}),
        )

        await pipeline.execute()
        return False

    async def get_job_status(self, task_id: str) -> QueuedTask | None:
        redis_client = await self.get_redis()
        task_key = f"{self.task_key_prefix}{task_id}"
        job_data = await redis_client.hgetall(task_key)
        if not job_data:
            return None
        return QueuedTask.from_redis_dict(job_data)

    def get_job_status_sync(self, task_id: str) -> QueuedTask | None:
        """Sync wrapper for get_job_status"""
        return async_to_sync(self.get_job_status)(task_id)

    async def listen_for_retries(self):
        redis_client = await self.get_redis()

        # Enable keyspace notifications for expired keys
        await redis_client.config_set("notify-keyspace-events", "Ex")

        pubsub = redis_client.pubsub()
        await pubsub.subscribe("__keyevent@0__:expired")

        async for message in pubsub.listen():
            if message["type"] == "message":
                key = message["data"]
                if key.startswith("cv:retry:"):
                    task_id = key.replace("cv:retry:", "")
                    # Re-enqueue job immediately
                    task_key = f"{self.task_key_prefix}{task_id}"
                    job_data = await redis_client.hgetall(task_key)
                    if job_data:
                        await redis_client.xadd(
                            self.job_stream,
                            {
                                "task_id": task_id,
                                "uid": job_data.get("uid", ""),
                                "priority": "1",  # Higher priority for retries
                                "timestamp": str(time.time()),
                            },
                        )

    async def cleanup_expired_jobs(self, max_age_hours: int = 24) -> int:
        redis_client = await self.get_redis()
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cutoff_timestamp = cutoff_time.isoformat()
        pattern = f"{self.task_key_prefix}*"
        expired_jobs = []

        async for key in redis_client.scan_iter(match=pattern):
            job_data = await redis_client.hgetall(key)
            if job_data.get("enqueued_at", "") < cutoff_timestamp:
                expired_jobs.append(key)

        if expired_jobs:
            await redis_client.delete(*expired_jobs)
        return len(expired_jobs)

    async def get_queue_stats(self) -> dict[str, Any]:
        try:
            redis_client = await self.get_redis()
            stream_info = await redis_client.xinfo_stream(self.job_stream)

            active_jobs = 0
            async for _ in redis_client.scan_iter(match=f"{self.task_key_prefix}*"):
                active_jobs += 1

            memory_info = await redis_client.info("memory")

            stats = {
                "stream_length": stream_info.get("length", 0),
                "cleanup_queue_length": await redis_client.llen(self.cleanup_queue),
                "scheduled_retries": await redis_client.zcard(self.retry_set),
                "active_jobs": active_jobs,
                "redis_memory_usage": int(memory_info.get("used_memory", 0)),
            }
            return stats
        except Exception as e:
            logger.error("Error getting queue stats: %s", e)
            return {}

    async def schedule_cleanup(self, cleanup_task: CleanupTask) -> None:
        """Schedule a cleanup task for a completed job."""
        redis_client = await self.get_redis()
        cleanup_data = {"uid": cleanup_task.uid, "cleanup_time": cleanup_task.cleanup_time}
        await redis_client.rpush(self.cleanup_queue, json.dumps(cleanup_data))

    async def get_cleanup_tasks(self) -> list[CleanupTask]:
        """Get all cleanup tasks from the queue."""
        redis_client = await self.get_redis()
        tasks = []
        cleanup_items = await redis_client.lrange(self.cleanup_queue, 0, -1)
        for item in cleanup_items:
            try:
                data = json.loads(item)
                tasks.append(CleanupTask(uid=data["uid"], cleanup_time=data["cleanup_time"]))
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning("Invalid cleanup task data: %s, error: %s", item, e)
        return tasks

    async def remove_cleanup_task(self, uid: str) -> bool:
        """Remove a cleanup task for a specific job."""
        redis_client = await self.get_redis()
        cleanup_items = await redis_client.lrange(self.cleanup_queue, 0, -1)
        for item in cleanup_items:
            try:
                task = json.loads(item)
                if task.get("uid") == uid:
                    await redis_client.lrem(self.cleanup_queue, 1, item)
                    return True
            except json.JSONDecodeError:
                continue
        return False

    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            self.redis = None
