import logging
import os
from collections.abc import Sequence
from typing import Any, Literal

from django.conf import settings
from pydantic_ai import Agent
from pydantic_ai.messages import BinaryContent, ImageUrl
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import UsageLimits

logger = logging.getLogger(__name__)

LLMMode = Literal["text", "ocr"]


class LLMService:
    def __init__(
        self,
        system_prompt: str,
        output_type: type,
        mode: LLMMode = "text",
    ):
        self.mode = mode
        self.model = self._create_model(mode)
        self.agent = Agent(
            model=self.model,
            output_type=output_type,
            system_prompt=system_prompt,
            retries=settings.MAX_RETRIES,
        )

    def _create_model(self, mode: LLMMode) -> str:
        if mode == "text":
            provider = settings.TEXT_LLM_PROVIDER
            model_name = settings.TEXT_LLM_MODEL
            api_key = settings.TEXT_LLM_API_KEY
            base_url = settings.TEXT_LLM_BASE_URL
        else:  # "ocr"
            provider = settings.OCR_LLM_PROVIDER
            model_name = settings.OCR_LLM_MODEL
            api_key = settings.OCR_LLM_API_KEY
            base_url = settings.OCR_LLM_BASE_URL

        env_key_name = f"{provider.upper()}_API_KEY"
        os.environ[env_key_name] = api_key

        # Handle custom base URL if provided
        if base_url:
            env_base_url_name = f"{provider.upper()}_BASE_URL"
            os.environ[env_base_url_name] = base_url

        return f"{provider}:{model_name}"  # pydantic-ai compliant

    async def run(self, prompt: str | Sequence[str | ImageUrl | BinaryContent], temperature: float = 0.1) -> Any:
        model_settings = ModelSettings(temperature=temperature, parallel_tool_calls=False)

        usage_limits = UsageLimits(
            request_limit=settings.LLM_REQUEST_LIMIT,
            request_tokens_limit=settings.LLM_REQUEST_TOKENS_LIMIT,
        )

        try:
            # https://ai.pydantic.dev/api/run/
            result = await self.agent.run(user_prompt=prompt, model_settings=model_settings, usage_limits=usage_limits)

            logger.info(f"LLM usage ({self.mode}): {result.usage()}")

            return result.output
        except Exception as e:
            logger.error(f"Unexpected error in LLM service ({self.mode} mode): {e}")
            raise
