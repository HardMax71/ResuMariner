import asyncio
import json
import logging
import os
import time
import uuid
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

import redis.asyncio as aioredis
from django.conf import settings

from processor.models import QueuedTask

logger = logging.getLogger(__name__)


class RedisJobQueue:
    def __init__(self):
        self.redis_pool = aioredis.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            max_connections=30,
            decode_responses=True,
        )
        self.job_stream = "cv:jobs:stream"
        self.consumer_group = "workers"
        self.consumer_name = f"worker-{os.getenv('WORKER_ID', '1')}"
        self.job_key_prefix = settings.REDIS_JOB_PREFIX
        self.task_key_prefix = "cv:task:"
        self.retry_set = "cv:retry:scheduled"
        self.active_jobs_counter = "cv:stats:active_jobs"
        self.pubsub = None

    async def enqueue_job(self, uid: str, file_path: str, parsed_doc: dict[str, Any]) -> str:
        redis_client = await self.get_redis()
        task_id = str(uuid.uuid4())

        task = QueuedTask(
            task_id=task_id,
            uid=uid,
            file_path=file_path,
            parsed_doc=parsed_doc,
            retries=0,
        )

        task_key = f"{self.task_key_prefix}{task_id}"
        redis_dict = task.to_redis_dict()

        pipeline = redis_client.pipeline()
        pipeline.hset(task_key, mapping=redis_dict)  # type: ignore[arg-type]
        pipeline.expire(task_key, settings.REDIS_PROCESSING_JOB_TTL)

        # Add to stream for instant delivery
        stream_data = {"task_id": task_id, "uid": uid, "timestamp": str(time.time())}
        pipeline.xadd(self.job_stream, stream_data)

        pipeline.incr(self.active_jobs_counter)
        pipeline.publish("cv:jobs:new", task_id)

        await pipeline.execute()
        return task_id

    async def get_redis(self) -> aioredis.Redis:
        redis = aioredis.Redis(connection_pool=self.redis_pool)

        try:
            await redis.xgroup_create(self.job_stream, self.consumer_group, id="0", mkstream=True)
        except aioredis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise

        await self._cleanup_stale_consumers(redis)
        return redis

    async def _cleanup_stale_consumers(self, redis: aioredis.Redis):
        try:
            groups = await redis.xinfo_groups(self.job_stream)
            for group in groups:
                if group["name"] == self.consumer_group:
                    consumers = await redis.xinfo_consumers(self.job_stream, self.consumer_group)
                    for consumer in consumers:
                        idle_time = consumer.get("idle", 0)
                        if idle_time > 300000 and consumer["name"] != self.consumer_name:
                            await redis.xgroup_delconsumer(self.job_stream, self.consumer_group, consumer["name"])
                            logger.info(f"Removed stale consumer: {consumer['name']}")
        except Exception as e:
            logger.warning(f"Failed to cleanup consumers: {e}")

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
                redis_client = await self.get_redis()

    async def mark_job_processing(self, task_id: str, uid: str) -> bool:
        redis_client = await self.get_redis()
        # Just publish the processing event for real-time updates
        await redis_client.publish(
            f"cv:job:{uid}:status", json.dumps({"status": "processing", "timestamp": datetime.now().isoformat()})
        )
        return True

    async def mark_job_completed(self, task_id: str, uid: str, result: dict[str, Any]) -> bool:
        redis_client = await self.get_redis()
        task_key = f"{self.task_key_prefix}{task_id}"

        pipeline = redis_client.pipeline()
        pipeline.expire(task_key, settings.REDIS_COMPLETED_JOB_TTL)
        pipeline.decr(self.active_jobs_counter)
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
        if retry and retries < settings.REDIS_MAX_RETRIES:
            retries += 1
            delay = min(60 * (2**retries), 300)

            pipeline = redis_client.pipeline()
            pipeline.hset(task_key, "retries", retries)
            pipeline.expire(task_key, settings.REDIS_PROCESSING_JOB_TTL)
            pipeline.zadd(self.retry_set, {task_id: time.time() + delay})
            pipeline.setex(f"cv:retry:{task_id}", delay, uid)

            await pipeline.execute()
            return True

        pipeline = redis_client.pipeline()
        pipeline.expire(task_key, settings.REDIS_FAILED_JOB_TTL)
        pipeline.decr(self.active_jobs_counter)
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
                                "timestamp": str(time.time()),
                            },
                        )

    async def get_queue_stats(self) -> dict[str, Any]:
        try:
            redis_client = await self.get_redis()
            stream_info = await redis_client.xinfo_stream(self.job_stream)
            active_jobs = await redis_client.get(self.active_jobs_counter) or "0"
            memory_info = await redis_client.info("memory")

            stats = {
                "stream_length": stream_info.get("length", 0),
                "scheduled_retries": await redis_client.zcard(self.retry_set),
                "active_jobs": int(active_jobs),
                "redis_memory_usage": int(memory_info.get("used_memory", 0)),
            }
            return stats
        except Exception as e:
            logger.error("Error getting queue stats: %s", e)
            return {}

    async def close(self):
        """Close Redis connection pool"""
        await self.redis_pool.disconnect()
