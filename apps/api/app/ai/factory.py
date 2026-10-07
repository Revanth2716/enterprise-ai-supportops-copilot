import logging
from typing import Dict, Any, Optional
from app.config import settings
from app.ai.base import AIProvider, ProviderResponse
from app.ai.mock_provider import MockProvider
from app.ai.ollama_provider import OllamaProvider
from app.ai.openai_provider import OpenAICompatibleProvider

logger = logging.getLogger(__name__)


def create_provider(provider_type: Optional[str] = None) -> AIProvider:
    ptype = (provider_type or settings.AI_PROVIDER).lower()

    if ptype == "ollama":
        return OllamaProvider(base_url=settings.OLLAMA_BASE_URL, model_name=settings.OLLAMA_MODEL)
    elif ptype in ("openai", "openai_compatible"):
        return OpenAICompatibleProvider(
            base_url=settings.OPENAI_BASE_URL,
            api_key=settings.OPENAI_API_KEY,
            model_name=settings.OPENAI_MODEL
        )
    else:
        return MockProvider(model_name=settings.AI_MODEL)


# Default fallback instance
fallback_mock_provider = MockProvider()


async def generate_with_fallback(
    prompt: str,
    system_prompt: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    preferred_provider: Optional[str] = None
) -> ProviderResponse:
    provider = create_provider(preferred_provider)

    if provider.name == "mock":
        return await provider.generate(prompt, system_prompt, context)

    try:
        return await provider.generate(prompt, system_prompt, context)
    except Exception as e:
        logger.warning(
            "primary_provider_failed_falling_back_to_mock",
            extra={"primary": provider.name, "error": str(e)}
        )
        resp = await fallback_mock_provider.generate(prompt, system_prompt, context)
        resp.fallback_used = True
        return resp
