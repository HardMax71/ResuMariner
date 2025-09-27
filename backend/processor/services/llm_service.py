import os
from typing import Any, Literal

from django.conf import settings
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings

LLMMode = Literal["text", "ocr"]


class LLMService:
    def __init__(
        self,
        system_prompt: str,
        result_type: type,
        mode: LLMMode = "text",
    ):
        self.mode = mode
        self.model = self._create_model(mode)
        self.result_type: type = result_type
        self.agent = Agent(
            model=self.model,  # type: ignore
            result_type=self.result_type,
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

    async def run(self, prompt: str | list, temperature: float = 0.1) -> Any:
        model_settings = ModelSettings(temperature=temperature, parallel_tool_calls=False)
        try:
            result = await self.agent.run(prompt, model_settings=model_settings)
            data = result.data
        except Exception:
            # Retry once on failure
            result = await self.agent.run(prompt, model_settings=model_settings)
            data = result.data

        # Ensure we return the correct type
        if isinstance(data, self.result_type):
            return data
        return data
