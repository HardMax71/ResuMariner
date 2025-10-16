import asyncio
import logging
import os
import signal

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

application = get_asgi_application()

logger = logging.getLogger(__name__)


def _cleanup_on_shutdown(signum, frame):
    from core.middleware import SearchServicesMiddleware

    if SearchServicesMiddleware._search_coordinator is not None:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(SearchServicesMiddleware._search_coordinator.close())
            else:
                loop.run_until_complete(SearchServicesMiddleware._search_coordinator.close())
            logger.info("SearchCoordinator cleanup completed")
        except Exception as e:
            logger.error("Error during SearchCoordinator cleanup: %s", e)


signal.signal(signal.SIGTERM, _cleanup_on_shutdown)
signal.signal(signal.SIGINT, _cleanup_on_shutdown)
