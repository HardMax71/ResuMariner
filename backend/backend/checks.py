import os

from django.conf import settings
from django.core.checks import Error, Tags, register


@register(Tags.security)
def check_secret_key(app_configs, **kwargs):
    """
    Check that SECRET_KEY is properly configured.

    This runs with:
    - python manage.py check
    - python manage.py check --deploy
    - python manage.py runserver (in development)
    - At application startup

    Skipped when:
    - Running tests (TESTING=true)
    """
    # Skip in test environment
    if os.environ.get("TESTING", "").lower() == "true":
        return []

    errors = []

    if not settings.SECRET_KEY or settings.SECRET_KEY == "insecure-default-key-for-development-only":
        errors.append(
            Error(
                "SECRET_KEY is not configured or using insecure default",
                hint="Set SECRET_KEY in your .env file to a strong random value (e.g., generated with Django's get_random_secret_key())",
                id="backend.E001",
            )
        )

    return errors


@register(Tags.security)
def check_api_security(app_configs, **kwargs):
    """
    Check that API security settings are configured.

    This runs with:
    - python manage.py check
    - python manage.py check --deploy
    - At application startup

    Skipped when:
    - Running tests (TESTING=true)
    """
    # Skip in test environment
    if os.environ.get("TESTING", "").lower() == "true":
        return []

    errors = []

    if not settings.API_KEY:
        errors.append(
            Error(
                "API_KEY is not configured",
                hint="Set API_KEY in your .env file or environment variables for API authentication",
                id="backend.E002",
            )
        )

    if not settings.JWT_SECRET:
        errors.append(
            Error(
                "JWT_SECRET is not configured",
                hint="Set JWT_SECRET in your .env file to a strong random value for JWT token signing",
                id="backend.E003",
            )
        )

    return errors


@register(Tags.compatibility)
def check_required_api_keys(app_configs, **kwargs):
    """
    Check that required LLM API keys are configured.

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
                hint="Set TEXT_LLM_API_KEY in your .env file or environment variables. Resume processing will fail without this.",
                id="backend.E004",
            )
        )

    if not settings.OCR_LLM_API_KEY:
        errors.append(
            Error(
                "OCR_LLM_API_KEY is not configured",
                hint="Set OCR_LLM_API_KEY in your .env file or environment variables. Image-based resume processing will fail without this.",
                id="backend.E005",
            )
        )

    return errors
