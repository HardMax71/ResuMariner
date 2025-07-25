import asyncio
import logging
import time
from typing import Dict, Any
from datetime import datetime

import httpx
import redis

from config import settings

logger = logging.getLogger(__name__)


class HealthChecker:
    """Comprehensive health check utility"""

    def __init__(self):
        self.redis_client = None
        self.http_client = httpx.AsyncClient(timeout=5.0)
        self.start_time = time.time()

    async def check_redis_health(self) -> Dict[str, Any]:
        """Check Redis connection health"""
        try:
            if not self.redis_client:
                self.redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    password=settings.REDIS_PASSWORD or None,
                    decode_responses=True,
                )

            start_time = time.time()

            # Test basic operations
            test_key = f"health_check:{int(time.time())}"
            self.redis_client.set(test_key, "test", ex=10)
            result = self.redis_client.get(test_key)
            self.redis_client.delete(test_key)

            response_time = time.time() - start_time

            # Get Redis info
            info = self.redis_client.info()

            return {
                "status": "healthy" if result == "test" else "unhealthy",
                "response_time_ms": round(response_time * 1000, 2),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
                "redis_version": info.get("redis_version", "unknown"),
            }

        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e), "response_time_ms": None}

    async def check_processing_service_health(self) -> Dict[str, Any]:
        """Check processing service health"""
        try:
            start_time = time.time()

            response = await self.http_client.get(
                f"{settings.PROCESSING_SERVICE_URL}/health"
            )

            response_time = time.time() - start_time

            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time_ms": round(response_time * 1000, 2),
                "status_code": response.status_code,
                "url": settings.PROCESSING_SERVICE_URL,
            }

        except Exception as e:
            logger.error(f"Processing service health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": None,
                "url": settings.PROCESSING_SERVICE_URL,
            }

    async def check_storage_service_health(self) -> Dict[str, Any]:
        """Check storage service health"""
        try:
            start_time = time.time()

            response = await self.http_client.get(
                f"{settings.STORAGE_SERVICE_URL}/health"
            )

            response_time = time.time() - start_time

            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time_ms": round(response_time * 1000, 2),
                "status_code": response.status_code,
                "url": settings.STORAGE_SERVICE_URL,
            }

        except Exception as e:
            logger.error(f"Storage service health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": None,
                "url": settings.STORAGE_SERVICE_URL,
            }

    async def check_queue_health(self) -> Dict[str, Any]:
        """Check job queue health"""
        try:
            if not self.redis_client:
                await self.check_redis_health()

            # Get queue statistics
            processing_queue_size = self.redis_client.llen(settings.REDIS_JOB_QUEUE)
            cleanup_queue_size = self.redis_client.llen(settings.REDIS_CLEANUP_QUEUE)

            # Check for stuck jobs (jobs processing for too long)
            stuck_jobs = 0
            processing_pattern = f"{settings.REDIS_JOB_PREFIX}*:processing"
            processing_keys = self.redis_client.keys(processing_pattern)

            current_time = time.time()
            for key in processing_keys:
                job_data = self.redis_client.hgetall(key)
                if job_data and "started_at" in job_data:
                    started_at = float(job_data["started_at"])
                    if current_time - started_at > settings.REDIS_JOB_TIMEOUT:
                        stuck_jobs += 1

            return {
                "status": "healthy",
                "processing_queue_size": processing_queue_size,
                "cleanup_queue_size": cleanup_queue_size,
                "stuck_jobs": stuck_jobs,
                "queue_prefix": settings.REDIS_JOB_PREFIX,
            }

        except Exception as e:
            logger.error(f"Queue health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}

    async def check_disk_space(self) -> Dict[str, Any]:
        """Check disk space for upload directory"""
        try:
            import shutil

            total, used, free = shutil.disk_usage(settings.UPLOAD_DIR)

            free_percent = (free / total) * 100
            used_percent = (used / total) * 100

            status = "healthy"
            if free_percent < 10:
                status = "critical"
            elif free_percent < 20:
                status = "warning"

            return {
                "status": status,
                "total_bytes": total,
                "used_bytes": used,
                "free_bytes": free,
                "free_percent": round(free_percent, 2),
                "used_percent": round(used_percent, 2),
                "path": settings.UPLOAD_DIR,
            }

        except Exception as e:
            logger.error(f"Disk space check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}

    async def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get comprehensive health check results"""
        start_time = time.time()

        # Run all health checks concurrently
        health_results = await asyncio.gather(
            self.check_redis_health(),
            self.check_processing_service_health(),
            self.check_storage_service_health(),
            self.check_queue_health(),
            self.check_disk_space(),
            return_exceptions=True,
        )

        # Convert to list for modification and handle exceptions
        health_checks = list(health_results)
        for i, result in enumerate(health_checks):
            if isinstance(result, Exception):
                health_checks[i] = {"status": "unhealthy", "error": str(result)}

        redis_health, processing_health, storage_health, queue_health, disk_health = (
            health_checks
        )

        # Determine overall status
        all_statuses = [
            redis_health.get("status", "unhealthy")
            if isinstance(redis_health, dict)
            else "unhealthy",
            processing_health.get("status", "unhealthy")
            if isinstance(processing_health, dict)
            else "unhealthy",
            storage_health.get("status", "unhealthy")
            if isinstance(storage_health, dict)
            else "unhealthy",
            queue_health.get("status", "unhealthy")
            if isinstance(queue_health, dict)
            else "unhealthy",
            disk_health.get("status", "unhealthy")
            if isinstance(disk_health, dict)
            else "unhealthy",
        ]

        if all(status == "healthy" for status in all_statuses):
            overall_status = "healthy"
        elif any(status == "critical" for status in all_statuses):
            overall_status = "critical"
        elif any(status == "warning" for status in all_statuses):
            overall_status = "warning"
        else:
            overall_status = "unhealthy"

        total_time = time.time() - start_time

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "check_duration_ms": round(total_time * 1000, 2),
            "service": "cv-intake-service",
            "version": "1.0.0",
            "checks": {
                "redis": redis_health,
                "processing_service": processing_health,
                "storage_service": storage_health,
                "queue": queue_health,
                "disk": disk_health,
            },
        }

    async def get_readiness_check(self) -> Dict[str, Any]:
        """Get readiness check (essential services only)"""
        try:
            # Check only essential services for readiness
            redis_health = await self.check_redis_health()

            is_ready = redis_health.get("status") == "healthy"

            return {
                "ready": is_ready,
                "timestamp": datetime.utcnow().isoformat(),
                "service": "cv-intake-service",
                "checks": {"redis": redis_health},
            }

        except Exception as e:
            logger.error(f"Readiness check failed: {str(e)}")
            return {
                "ready": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "service": "cv-intake-service",
            }

    async def get_liveness_check(self) -> Dict[str, Any]:
        """Get liveness check (basic service health)"""
        try:
            # Basic liveness check
            return {
                "alive": True,
                "timestamp": datetime.utcnow().isoformat(),
                "service": "cv-intake-service",
                "uptime_seconds": time.time()
                - getattr(self, "start_time", time.time()),
            }

        except Exception as e:
            logger.error(f"Liveness check failed: {str(e)}")
            return {
                "alive": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "service": "cv-intake-service",
            }

    def __del__(self):
        """Cleanup"""
        if hasattr(self, "http_client"):
            asyncio.create_task(self.http_client.aclose())


# Global health checker instance
health_checker = HealthChecker()
health_checker.start_time = time.time()
