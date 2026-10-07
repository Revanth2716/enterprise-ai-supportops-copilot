from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class ProviderResponse(BaseModel):
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: int = 0
    estimated_cost_usd: float = 0.000000
    provider_name: str
    model_name: str
    fallback_used: bool = False


class AIProvider(ABC):
    """
    Abstract AI Provider interface supporting deterministic mock,
    local Ollama, and OpenAI-compatible inference backends.
    """

    def __init__(self, name: str, model_name: str):
        self.name = name
        self.model_name = model_name

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ProviderResponse:
        pass
