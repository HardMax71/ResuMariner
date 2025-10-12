from collections.abc import Callable

from .base import BaseWorker
from .processing import ProcessingWorker

WORKER_REGISTRY: dict[str, Callable[[], BaseWorker]] = {
    "processing": ProcessingWorker,
}


def get_worker(worker_type: str) -> BaseWorker:
    if worker_type not in WORKER_REGISTRY:
        raise ValueError(f"Unknown worker type: {worker_type}")
    worker_class = WORKER_REGISTRY[worker_type]
    return worker_class()
