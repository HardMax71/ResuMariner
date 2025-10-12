import os

from django.conf import settings
from django.core.checks import Error, Tags, register


@register(Tags.compatibility)
def check_required_api_keys(app_configs, **kwargs):
    """
    Check that required API keys are configured.

    This runs with:
    - python manage.py check
    - python manage.py runserver (in development)
    - At application startup

    Skipped when:
    - Running tests (TESTING=true)
    - Running migrations (detected automatically)
    """
    # Skip in test environment
    if os.environ.get("TESTING", "").lower() == "true":
        return []

    # Skip during migrations (Django sets this)
    if kwargs.get("databases") is False:
        return []

    errors = []

    if not settings.TEXT_LLM_API_KEY:
        errors.append(
            Error(
                "TEXT_LLM_API_KEY is not configured",
                hint="Set TEXT_LLM_API_KEY in your .env file or environment variables",
                id="backend.E001",
            )
        )

    if not settings.OCR_LLM_API_KEY:
        errors.append(
            Error(
                "OCR_LLM_API_KEY is not configured",
                hint="Set OCR_LLM_API_KEY in your .env file or environment variables",
                id="backend.E002",
            )
        )

    return errors
