import logging

import httpx
import redis.asyncio as aioredis
from neo4j.exceptions import Neo4jError
from pydantic import ValidationError as PydanticValidationError
from qdrant_client.http.exceptions import UnexpectedResponse as QdrantError
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that sanitizes error messages to prevent internal details leakage.

    Handles both DRF exceptions and infrastructure exceptions, always returning a Response object.
    """

    # First, try DRF's default handler for APIException instances
    if isinstance(exc, APIException):
        response = drf_exception_handler(exc, context)
        if response is not None:
            return response

    # Handle httpx exceptions (external API calls)
    if isinstance(exc, httpx.TimeoutException):
        logger.error("Request timeout: %s", exc, exc_info=True)
        return Response(
            {"detail": "Request timeout, please try again"},
            status=status.HTTP_504_GATEWAY_TIMEOUT,
        )

    if isinstance(exc, httpx.HTTPStatusError):
        logger.error("HTTP error from external service: %s - %s", exc.response.status_code, exc, exc_info=True)
        if exc.response.status_code == 429:
            return Response(
                {"detail": "Rate limit exceeded, please try again later"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        return Response(
            {"detail": "External service error"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if isinstance(exc, httpx.HTTPError):
        logger.error("HTTP client error: %s", exc, exc_info=True)
        return Response(
            {"detail": "External service unavailable"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # Handle Redis exceptions
    if isinstance(exc, (aioredis.ConnectionError, aioredis.TimeoutError)):
        logger.error("Redis connection error: %s", exc, exc_info=True)
        return Response(
            {"detail": "Service temporarily unavailable"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if isinstance(exc, aioredis.ResponseError):
        logger.error("Redis error: %s", exc, exc_info=True)
        return Response(
            {"detail": "Service temporarily unavailable"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # Handle Neo4j exceptions
    if isinstance(exc, Neo4jError):
        logger.error("Neo4j database error: %s", exc, exc_info=True)
        return Response(
            {"detail": "Database temporarily unavailable"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # Handle Qdrant exceptions
    if isinstance(exc, QdrantError):
        logger.error("Qdrant vector database error: %s", exc, exc_info=True)
        return Response(
            {"detail": "Search service temporarily unavailable"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # Handle Pydantic validation errors
    if isinstance(exc, PydanticValidationError):
        logger.error("Pydantic validation error: %s", exc, exc_info=True)
        return Response(
            {"detail": "Invalid data format"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Handle file operation errors
    if isinstance(exc, (FileNotFoundError, OSError)):
        logger.error("File operation error: %s", exc, exc_info=True)
        return Response(
            {"detail": "File operation failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Handle permission errors
    if isinstance(exc, PermissionError):
        logger.error("Permission denied: %s", exc, exc_info=True)
        return Response(
            {"detail": "Operation not permitted"},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Handle ValueError - don't expose internal details
    if isinstance(exc, ValueError):
        logger.error("Value error: %s", exc, exc_info=True)
        return Response(
            {"detail": "Invalid request"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Handle KeyError - don't expose internal details
    if isinstance(exc, KeyError):
        logger.error("Missing required key: %s", exc, exc_info=True)
        return Response(
            {"detail": "Missing required field"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Catch-all for unexpected exceptions - don't expose internal details
    logger.error("Unexpected error: %s", exc, exc_info=True)
    return Response(
        {"detail": "Internal server error"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
