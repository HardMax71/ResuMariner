import asyncio
import logging
import signal
from abc import ABC, abstractmethod


class BaseWorker(ABC):
    """Abstract base class for background workers with graceful shutdown."""

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

    async def run(self) -> None:
        """Main entry point that starts worker lifecycle: startup, tasks, shutdown."""
        await self.startup()
        self.logger.info("Starting %s worker", self.name)

        self.tasks = await self.create_tasks()

        try:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        except asyncio.CancelledError:
            self.logger.info("%s worker cancelled", self.name)

        await self.shutdown()
        self.logger.info("%s worker stopped", self.name)

    @abstractmethod
    async def startup(self) -> None:
        pass

    @abstractmethod
    async def create_tasks(self) -> list[asyncio.Task]:
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        pass

    async def handle_error(self, error: Exception) -> None:
        self.logger.exception("Worker error: %s", error)
