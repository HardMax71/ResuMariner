import asyncio
import logging
import signal
from abc import ABC, abstractmethod


class BaseWorker(ABC):
    def __init__(self):
        self.name = "worker"
        self.running = True
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self.tasks: list[asyncio.Task] = []
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        self.logger.info("Received signal %s, shutting down gracefully...", signum)
        self.running = False
        for task in self.tasks:
            task.cancel()

    async def run(self):
        await self.startup()
        self.logger.info("Starting %s worker", self.name)

        # Start all concurrent tasks
        self.tasks = await self.create_tasks()

        try:
            # Wait for all tasks to complete
            await asyncio.gather(*self.tasks, return_exceptions=True)
        except asyncio.CancelledError:
            self.logger.info("%s worker cancelled", self.name)

        await self.shutdown()
        self.logger.info("%s worker stopped", self.name)

    @abstractmethod
    async def startup(self):
        """Override for async initialization"""
        pass

    @abstractmethod
    async def create_tasks(self) -> list[asyncio.Task]:
        """Create and return all worker tasks to run concurrently"""
        pass

    @abstractmethod
    async def shutdown(self):
        """Override for cleanup"""
        pass

    async def handle_error(self, error: Exception):
        self.logger.exception("Worker error: %s", error)
