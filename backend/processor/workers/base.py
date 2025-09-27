import asyncio
import logging
import signal
from abc import ABC, abstractmethod


class BaseWorker(ABC):
    def __init__(self):
        self.name = "worker"
        self.sleep_interval = 1.0
        self.running = True
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        self.logger.info("Received signal %s, shutting down gracefully...", signum)
        self.running = False

    async def run(self):
        # Call startup only if it's overridden
        await self.startup()
        self.logger.info("Starting %s worker", self.name)

        while self.running:
            try:
                has_work = await self.process_iteration()
                if not has_work:
                    await asyncio.sleep(self.sleep_interval)
            except Exception as e:
                await self.handle_error(e)
                await asyncio.sleep(self.get_error_backoff())

        await self.shutdown()
        self.logger.info("%s worker stopped", self.name)

    @abstractmethod
    async def startup(self):
        """Override only if you need async initialization"""
        pass

    @abstractmethod
    async def process_iteration(self) -> bool:
        """Process one iteration of work. Return True if work was done."""
        pass

    @abstractmethod
    async def shutdown(self):
        """Override only if you have resources to clean up"""
        pass

    async def handle_error(self, error: Exception):
        self.logger.exception("Worker error: %s", error)

    def get_error_backoff(self) -> float:
        return 5.0
