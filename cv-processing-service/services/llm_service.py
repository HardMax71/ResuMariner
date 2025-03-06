import os
from typing import TypeVar, Generic, Type, Optional

from pydantic_ai import Agent
from pydantic_ai.models import infer_model
from pydantic_ai.settings import ModelSettings

from config import settings
from utils.errors import LLMServiceError

# Generic type for result models
T = TypeVar('T')


class LLMService(Generic[T]):
    """Base service for LLM interactions"""

    def __init__(self, result_type: Type[T], system_prompt: str):
        """Initialize the LLM service"""
        try:
            # First - setting key value to env vars
            os.environ[f"{settings.LLM_PROVIDER.upper()}_API_KEY"] = settings.LLM_API_KEY

            # Special case for custom base URLs
            if settings.LLM_BASE_URL:
                from pydantic_ai.models.openai import OpenAIModel
                self.model = OpenAIModel(
                    model_name=settings.LLM_MODEL,
                    base_url=settings.LLM_BASE_URL,
                    api_key=settings.LLM_API_KEY
                )
            else:
                # For all other providers, use infer_model and pass API key
                model_string = f"{settings.LLM_PROVIDER}:{settings.LLM_MODEL}"
                model = infer_model(model_string)

                # Set the API key for the model
                if hasattr(model, 'api_key'):
                    model.api_key = settings.LLM_API_KEY
                elif hasattr(model, 'client') and hasattr(model.client, 'api_key'):
                    model.client.api_key = settings.LLM_API_KEY

                self.model = model

            # Create the agent
            self.agent = Agent(
                model=self.model,
                result_type=result_type,
                system_prompt=system_prompt
            )
        except Exception as e:
            raise LLMServiceError(f"Failed to initialize LLM service: {str(e)}")

    async def run(self, prompt: str, temperature: Optional[float] = None) -> T:
        """Run inference with the LLM asynchronously"""
        try:
            temp = temperature if temperature is not None else settings.TEMPERATURE

            model_settings = ModelSettings(
                temperature=temp,
                parallel_tool_calls=False
            )

            result = await self.agent.run(
                prompt,
                model_settings=model_settings
            )

            return result.data

        except Exception as e:
            raise LLMServiceError(f"LLM inference failed: {str(e)}")