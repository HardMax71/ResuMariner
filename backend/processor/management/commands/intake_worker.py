import asyncio

from django.core.management.base import BaseCommand

from ...workers import WORKER_REGISTRY, get_worker


class Command(BaseCommand):
    help = "Run intake worker"

    def add_arguments(self, parser):
        parser.add_argument(
            "worker_type",
            nargs="?",
            default="processing",
            choices=list(WORKER_REGISTRY.keys())
        )

    def handle(self, *args, **options):
        worker_type = options["worker_type"]
        worker = get_worker(worker_type)
        asyncio.run(worker.run())
