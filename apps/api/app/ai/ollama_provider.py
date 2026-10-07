import time
import httpx
from typing import Dict, Any, Optional
from app.ai.base import AIProvider, ProviderResponse


class OllamaProvider(AIProvider):
    """
    Local Ollama Inference Provider.
    Calls local Ollama daemon (e.g. http://localhost:11434).
    """

    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "deepseek-r1:8b"):
        super().__init__(name="ollama", model_name=model_name)
        self.base_url = base_url.rstrip("/")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ProviderResponse:
        start_time = time.perf_counter()

        full_prompt = f"System: {system_prompt}\n\nContext: {context}\n\nUser: {prompt}" if system_prompt else prompt

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False
                }
            )
            resp.raise_for_status()
            data = resp.json()

        content = data.get("response", "")
        prompt_tokens = data.get("prompt_eval_count", len(prompt.split()) + 50)
        completion_tokens = data.get("eval_count", len(content.split()))
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        return ProviderResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=elapsed_ms,
            estimated_cost_usd=0.000000,
            provider_name=self.name,
            model_name=self.model_name,
            fallback_used=False
        )
