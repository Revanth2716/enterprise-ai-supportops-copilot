import time
import httpx
from typing import Dict, Any, Optional
from app.ai.base import AIProvider, ProviderResponse


class OpenAICompatibleProvider(AIProvider):
    """
    OpenAI-Compatible endpoint provider (vLLM, Ollama OpenAI API, or OpenAI).
    """

    def __init__(
        self,
        base_url: str = "https://api.openai.com/v1",
        api_key: Optional[str] = None,
        model_name: str = "gpt-4o-mini"
    ):
        super().__init__(name="openai_compatible", model_name=model_name)
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ProviderResponse:
        start_time = time.perf_counter()

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": f"Context: {context}\n\nQuery: {prompt}"})

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": 0.2
                }
            )
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]["message"]
        content = choice.get("content", "")
        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", len(prompt.split()) + 50)
        completion_tokens = usage.get("completion_tokens", len(content.split()))

        # Estimated cost calculation ($0.15/1M input, $0.60/1M output for gpt-4o-mini)
        cost = (prompt_tokens * 0.00000015) + (completion_tokens * 0.00000060)
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        return ProviderResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=elapsed_ms,
            estimated_cost_usd=round(cost, 6),
            provider_name=self.name,
            model_name=self.model_name,
            fallback_used=False
        )
