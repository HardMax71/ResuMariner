from typing import Any, TypeVar, Generic

from config import settings
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.settings import ModelSettings
from utils.errors import LLMServiceError

# Generic type for result models
T = TypeVar('T')


class LLMService(Generic[T]):
    """Base service for LLM interactions"""

    def __init__(self, result_type: Any, system_prompt: str):
        """Initialize the LLM service"""
        try:
            self.model = OpenAIModel(
                settings.LLM_MODEL,
                api_key=settings.active_api_key
            )

            self.agent = Agent(
                model=self.model,
                result_type=result_type,
                system_prompt=system_prompt
            )
        except Exception as e:
            raise LLMServiceError(f"Failed to initialize LLM service: {str(e)}")

    async def run(self, prompt: str, temperature: float = None) -> T:
        """Run inference with the LLM asynchronously"""
        try:
            temp = temperature if temperature is not None else settings.TEMPERATURE

            model_settings = ModelSettings(
                temperature=temp,
                parallel_tool_calls=False
            )

            # Use await with agent.run
            result = await self.agent.run(
                prompt,
                model_settings=model_settings
            )

            return result.data

        except Exception as e:
            raise LLMServiceError(f"LLM inference failed: {str(e)}")