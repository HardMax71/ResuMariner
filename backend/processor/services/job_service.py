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
from rest_framework.exceptions import NotFound

from backend.settings import (
    REDIS_MAX_RETRIES,
    REDIS_RETRY_BASE_DELAY,
    REDIS_RETRY_MAX_DELAY,
    REDIS_SCAN_BATCH_SIZE,
    REDIS_STREAM_BLOCK_MS,
    REDIS_STREAM_READ_COUNT,
)

from ..models import Job, JobExecution
from ..serializers import JobStatus

logger = logging.getLogger(__name__)


class JobService:
    """Manages resume processing jobs using Redis for queue and state tracking."""

    _redis_pool: aioredis.ConnectionPool | None = None
    _pool_lock = asyncio.Lock()
    _initialized: bool = False

    def __init__(self) -> None:
        self.prefix = settings.REDIS_JOB_PREFIX
        self.job_stream = "resume:jobs:stream"
        self.consumer_group = "workers"
        self.consumer_name = f"worker-{os.getenv('WORKER_ID', '1')}"
        self.execution_key_prefix = "resume:execution:"
        self.active_jobs_counter = "resume:stats:active_jobs"
        self._redis_client: aioredis.Redis | None = None

    @classmethod
    async def initialize(cls) -> None:
        async with cls._pool_lock:
            if cls._initialized:
                return

            cls._redis_pool = aioredis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
                decode_responses=True,
            )

            temp_client = aioredis.Redis(connection_pool=cls._redis_pool)

            await temp_client.config_set("notify-keyspace-events", "Ex")
            logger.info("Configured Redis keyspace notifications")
            try:
                await temp_client.xgroup_create("resume:jobs:stream", "workers", id="0", mkstream=True)
                logger.info("Created Redis stream consumer group")
            except aioredis.ResponseError as e:
                if "BUSYGROUP" not in str(e):
                    raise
                logger.debug("Redis stream consumer group already exists")

            await temp_client.close()
            cls._initialized = True
            logger.info("JobService initialized")

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis_client is None:
            if not JobService._initialized:
                await JobService.initialize()
            self._redis_client = aioredis.Redis(connection_pool=JobService._redis_pool)
        return self._redis_client

    def _get_key(self, uid: str) -> str:
        return f"{self.prefix}{uid}"

    async def create_job(self, file_path: str, uid: str) -> Job:
        """Create a new job for resume processing."""
        job = Job(uid=uid, file_path=file_path)
        redis = await self._get_redis()
        await redis.set(self._get_key(uid), job.model_dump_json(), ex=settings.REDIS_JOB_TTL)
        logger.info("Created job %s", uid)
        return job

    async def get_job(self, uid: str) -> Job:
        """Get job status by uid."""
        redis = await self._get_redis()
        job_json = await redis.get(self._get_key(uid))
        if not job_json:
            raise NotFound("Job not found")
        return Job.model_validate_json(job_json)

    async def count_jobs(self) -> int:
        """Count total jobs in Redis with caching to avoid expensive SCAN on every request."""
        redis = await self._get_redis()

        # Try to get cached count (60-second cache)
        cache_key = "resume:stats:job_count_cache"
        cached = await redis.get(cache_key)
        if cached:
            return int(cached)

        # Perform SCAN to count (expensive operation)
        cursor = 0
        count = 0
        while True:
            cursor, keys = await redis.scan(cursor=cursor, match=f"{self.prefix}*", count=REDIS_SCAN_BATCH_SIZE)
            count += len(keys)
            if cursor == 0:
                break

        # Cache the result for 60 seconds
        await redis.setex(cache_key, 60, count)
        return count

    async def list_jobs(self, limit: int = 100, offset: int = 0) -> list[Job]:
        """List jobs with pagination."""
        redis = await self._get_redis()
        all_keys: list[str] = []
        cursor = 0

        target_count = offset + limit
        while len(all_keys) < target_count:
            cursor, keys = await redis.scan(cursor=cursor, match=f"{self.prefix}*", count=REDIS_SCAN_BATCH_SIZE)
            all_keys.extend(keys)
            if cursor == 0:
                break

        paginated_keys = all_keys[offset : offset + limit]
        if not paginated_keys:
            return []

        values = await redis.mget(paginated_keys)
        return [Job.model_validate_json(v) for v in values if v]

    async def update_job(self, uid: str, **updates) -> Job:
        job = await self.get_job(uid)

        if updates.get("status") in (JobStatus.COMPLETED, JobStatus.FAILED):
            updates["completed_at"] = datetime.now()

        updates["updated_at"] = datetime.now()
        job = job.model_copy(update=updates)

        redis = await self._get_redis()
        await redis.set(self._get_key(uid), job.model_dump_json(), ex=settings.REDIS_JOB_TTL)
        return job

    async def delete_job(self, uid: str) -> None:
        """Delete job from Redis."""
        redis = await self._get_redis()
        await redis.delete(self._get_key(uid))
        logger.info("Deleted job %s from Redis", uid)

    async def enqueue_job(self, uid: str, file_path: str, parsed_doc: dict[str, Any]) -> str:
        """Create and enqueue a new execution for a job.

        Returns:
            execution_id: Unique identifier for this execution attempt
        """
        redis_client = await self._get_redis()
        execution_id = str(uuid.uuid4())

        execution = JobExecution(
            execution_id=execution_id,
            job_uid=uid,
            file_path=file_path,
            parsed_doc=parsed_doc,
            attempt_number=1,
        )

        execution_key = f"{self.execution_key_prefix}{execution_id}"
        redis_dict = execution.model_dump()
        redis_dict["parsed_doc"] = json.dumps(redis_dict["parsed_doc"])

        pipeline = redis_client.pipeline()
        pipeline.hset(execution_key, mapping=redis_dict)  # type: ignore[arg-type]
        pipeline.expire(execution_key, settings.REDIS_JOB_TTL)
        stream_data = {"execution_id": execution_id, "uid": uid, "timestamp": str(time.time())}
        pipeline.xadd(self.job_stream, stream_data)
        pipeline.incr(self.active_jobs_counter)
        await pipeline.execute()
        return execution_id

    async def _reclaim_pending(self, redis_client: aioredis.Redis) -> AsyncIterator[JobExecution]:
        """Reclaim and yield pending messages for this consumer after reconnection."""
        result = await redis_client.xreadgroup(
            self.consumer_group, self.consumer_name, {self.job_stream: "0"}, count=100
        )
        if not result:
            return

        _, messages = result[0]
        if messages:
            logger.warning("Reclaiming %d pending messages after reconnection", len(messages))
            for msg_id, data in messages:
                execution = await self._process_stream_message(redis_client, msg_id, data)
                if execution:
                    yield execution

    async def consume_jobs(self) -> AsyncIterator[JobExecution]:
        """Consume job executions from Redis stream for worker processing."""
        redis_client = await self._get_redis()

        while True:
            try:
                result = await redis_client.xreadgroup(
                    self.consumer_group,
                    self.consumer_name,
                    {self.job_stream: ">"},
                    count=REDIS_STREAM_READ_COUNT,
                    block=REDIS_STREAM_BLOCK_MS,
                )

                if not result:
                    continue

                _, messages = result[0]

                for msg_id, data in messages:
                    execution = await self._process_stream_message(redis_client, msg_id, data)
                    if execution:
                        yield execution

            except aioredis.ConnectionError:
                logger.error("Redis connection lost, reconnecting...")
                await asyncio.sleep(1)
                redis_client = await self._get_redis()
                async for execution in self._reclaim_pending(redis_client):
                    yield execution

    async def _process_stream_message(
        self, redis_client: aioredis.Redis, msg_id: str, data: dict
    ) -> JobExecution | None:
        execution_id = data.get("execution_id")
        if not execution_id:
            logger.warning("Stream message %s missing execution_id, acking and skipping", msg_id)
            await redis_client.xack(self.job_stream, self.consumer_group, msg_id)
            return None

        execution_key = f"{self.execution_key_prefix}{execution_id}"
        execution_data = await redis_client.hgetall(execution_key)

        if not execution_data:
            logger.warning(
                "Execution data not found for execution_id %s, msg %s, acking and skipping", execution_id, msg_id
            )
            await redis_client.xack(self.job_stream, self.consumer_group, msg_id)
            return None

        await redis_client.xack(self.job_stream, self.consumer_group, msg_id)

        execution_data["parsed_doc"] = json.loads(execution_data["parsed_doc"])
        execution_data["attempt_number"] = int(execution_data.get("attempt_number", 1))
        return JobExecution.model_validate(execution_data)

    async def mark_execution_processing(self, execution_id: str, job_uid: str) -> bool:
        """Mark an execution as currently processing and update the Job status."""
        await self.update_job(job_uid, status=JobStatus.PROCESSING)
        return True

    async def mark_execution_completed(self, execution_id: str, job_uid: str, result: dict[str, Any]) -> bool:
        """Mark an execution as completed and update the Job status."""
        await self.update_job(job_uid, status=JobStatus.COMPLETED, result=result)
        redis_client = await self._get_redis()
        execution_key = f"{self.execution_key_prefix}{execution_id}"

        pipeline = redis_client.pipeline()
        pipeline.expire(execution_key, settings.REDIS_JOB_TTL)
        pipeline.decr(self.active_jobs_counter)
        await pipeline.execute()
        return True

    async def mark_execution_failed(self, execution_id: str, job_uid: str, error: str, retry: bool = True) -> bool:
        """Mark an execution as failed and optionally schedule a retry."""
        redis_client = await self._get_redis()
        execution_key = f"{self.execution_key_prefix}{execution_id}"
        execution_data = await redis_client.hgetall(execution_key)
        if not execution_data:
            return False

        attempt_number = int(execution_data.get("attempt_number", 1))
        if retry and attempt_number < REDIS_MAX_RETRIES:
            next_attempt = attempt_number + 1
            delay = min(REDIS_RETRY_BASE_DELAY * (2**attempt_number), REDIS_RETRY_MAX_DELAY)

            await self.update_job(
                job_uid, error=f"Attempt {attempt_number}/{REDIS_MAX_RETRIES} failed: {error}. Retrying in {delay}s..."
            )

            pipeline = redis_client.pipeline()
            pipeline.hset(execution_key, "attempt_number", next_attempt)
            pipeline.expire(execution_key, settings.REDIS_JOB_TTL)
            pipeline.setex(f"resume:retry:{execution_id}", delay, job_uid)
            await pipeline.execute()
            return True

        await self.update_job(job_uid, status=JobStatus.FAILED, error=error)
        pipeline = redis_client.pipeline()
        pipeline.expire(execution_key, settings.REDIS_JOB_TTL)
        pipeline.decr(self.active_jobs_counter)
        await pipeline.execute()
        return False

    async def listen_for_retries(self) -> None:
        """Listen for expired retry keys and re-enqueue failed executions.

        Flow:
        1. Subscribe to Redis keyspace notifications for expired keys
        2. When resume:retry:{execution_id} expires (after backoff delay), event fires
        3. Re-enqueue execution to stream for another attempt

        Requires: Redis config notify-keyspace-events = Ex
        """
        redis_client = await self._get_redis()
        pubsub = redis_client.pubsub()
        await pubsub.subscribe("__keyevent@0__:expired")

        async for message in pubsub.listen():
            if message["type"] == "message":
                key = message["data"]
                if key.startswith("resume:retry:"):
                    execution_id = key.replace("resume:retry:", "")
                    execution_key = f"{self.execution_key_prefix}{execution_id}"
                    execution_data = await redis_client.hgetall(execution_key)
                    if execution_data:
                        await redis_client.xadd(
                            self.job_stream,
                            {
                                "execution_id": execution_id,
                                "uid": execution_data.get("job_uid", ""),
                                "timestamp": str(time.time()),
                            },
                        )

    async def get_queue_stats(self) -> dict[str, Any]:
        """Get queue statistics including stream length and active jobs."""
        redis_client = await self._get_redis()
        stream_info = await redis_client.xinfo_stream(self.job_stream)
        active_jobs = await redis_client.get(self.active_jobs_counter) or "0"
        memory_info = await redis_client.info("memory")

        # Count scheduled retry jobs
        retry_keys = []
        cursor = 0
        while True:
            cursor, keys = await redis_client.scan(cursor=cursor, match="resume:retry:*", count=REDIS_SCAN_BATCH_SIZE)
            retry_keys.extend(keys)
            if cursor == 0:
                break

        queue_length = stream_info.get("length", 0)
        stats = {
            "stream_length": queue_length,
            "queue_length": queue_length,
            "scheduled_retries": len(retry_keys),
            "active_jobs": int(active_jobs),
            "redis_memory_usage": int(memory_info.get("used_memory", 0)),
        }
        return stats
