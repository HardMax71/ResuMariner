import asyncio
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from neomodel import adb

from core.database import create_graph_service, create_vector_service
from processor.serializers import JobStatus
from processor.services.cleanup_service import CleanupService
from processor.services.job_service import JobService


class Command(BaseCommand):
    help = "Clean up old jobs and associated resources"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days", type=int, default=settings.JOB_RETENTION_DAYS, help="Delete jobs older than this many days"
        )
        parser.add_argument("--all", action="store_true", help="Delete all completed/failed jobs regardless of age")
        parser.add_argument(
            "--dry-run", action="store_true", help="Show what would be deleted without actually deleting"
        )
        parser.add_argument("--force", action="store_true", help="Delete jobs even if still processing")

    def handle(self, *args, **options):
        days = options["days"]
        cleanup_all = options["all"]
        dry_run = options["dry_run"]
        force = options["force"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No actual deletions will occur"))

        asyncio.run(self._cleanup(days, cleanup_all, dry_run, force))

    async def _cleanup(self, days: int, cleanup_all: bool, dry_run: bool, force: bool):
        # Neo4j connection
        host = settings.NEO4J_URI.replace("bolt://", "")
        connection_url = f"bolt://{settings.NEO4J_USERNAME}:{settings.NEO4J_PASSWORD}@{host}"
        await adb.set_connection(url=connection_url)

        graph_db = create_graph_service()
        vector_db = create_vector_service()

        job_service = JobService()
        cleanup_service = CleanupService()

        jobs = await job_service.list_jobs(limit=10000)

        if cleanup_all:
            cutoff_date = None
            self.stdout.write("Processing ALL completed/failed jobs...")
        else:
            cutoff_date = datetime.now() - timedelta(days=days)
            self.stdout.write(f"Processing jobs older than {days} days (before {cutoff_date})...")

        total_deleted = 0
        total_skipped = 0

        for job in jobs:
            uid = job.uid
            status = job.status
            created_at = job.created_at

            should_delete = False

            if cleanup_all:
                if force or status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                    should_delete = True
            elif cutoff_date and created_at:
                if created_at < cutoff_date:
                    if force or status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                        should_delete = True

            if should_delete:
                if dry_run:
                    self.stdout.write(f"  Would delete: {uid} (status: {status}, created: {created_at})")
                else:
                    try:
                        success = await cleanup_service.cleanup_job(uid, graph_db, vector_db)
                        if success:
                            self.stdout.write(
                                self.style.SUCCESS(f"  Deleted: {uid} (status: {status}, created: {created_at})")
                            )
                            total_deleted += 1
                        else:
                            self.stdout.write(self.style.ERROR(f"  Failed to delete {uid}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  Failed to delete {uid}: {e}"))
            else:
                if status not in [JobStatus.COMPLETED, JobStatus.FAILED] and not force:
                    self.stdout.write(f"  Skipped: {uid} (still {status})")
                    total_skipped += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(f"\nDRY RUN: Would delete {total_deleted} jobs"))
        else:
            self.stdout.write(self.style.SUCCESS(f"\nDeleted {total_deleted} jobs, skipped {total_skipped}"))
