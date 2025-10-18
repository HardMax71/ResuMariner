import logging
import time
from collections.abc import Sequence
from typing import Literal

from django.conf import settings
from pydantic_ai import Agent
from pydantic_ai.messages import BinaryContent, ImageUrl
from pydantic_ai.run import AgentRunResult
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import UsageLimits

from core.metrics import LLM_API_CALLS, LLM_API_DURATION

logger = logging.getLogger(__name__)

LLMMode = Literal["text", "ocr"]


class LLMService[OutputT]:
    def __init__(
        self,
        system_prompt: str,
        output_type: type[OutputT],
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
        else:
            provider = settings.OCR_LLM_PROVIDER
            model_name = settings.OCR_LLM_MODEL

        return f"{provider}:{model_name}"

    async def run(
        self, prompt: str | Sequence[str | ImageUrl | BinaryContent], temperature: float = 0.1
    ) -> AgentRunResult[OutputT]:
        model_settings = ModelSettings(
            temperature=temperature,
            parallel_tool_calls=False,
            timeout=settings.REQUEST_TIMEOUT,
        )
        usage_limits = UsageLimits(
            request_limit=settings.LLM_REQUEST_LIMIT,
            request_tokens_limit=settings.LLM_REQUEST_TOKENS_LIMIT,
        )

        start_time = time.time()
        try:
            result = await self.agent.run(user_prompt=prompt, model_settings=model_settings, usage_limits=usage_limits)
            logger.info("LLM usage (%s): %s", self.mode, result.usage())

            LLM_API_CALLS.labels(mode=self.mode, status="success").inc()
            LLM_API_DURATION.labels(mode=self.mode).observe(time.time() - start_time)

            return result
        except Exception as e:
            logger.error("LLM API call failed (%s mode): %s", self.mode, e)
            LLM_API_CALLS.labels(mode=self.mode, status="error").inc()
            LLM_API_DURATION.labels(mode=self.mode).observe(time.time() - start_time)
            raise
