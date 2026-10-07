import pytest
from app.ai.mock_provider import MockProvider
from app.ai.factory import generate_with_fallback


@pytest.mark.asyncio
async def test_mock_provider_deterministic_response():
    provider = MockProvider()
    resp = await provider.generate(
        prompt="ACME invoice INV-1042 duplicate charge",
        context={"retrieved_chunks": [{"citation_token": "[Doc:Billing Policy#C1]"}]}
    )
    assert resp.provider_name == "mock"
    assert resp.estimated_cost_usd == 0.0
    assert "[Doc:Billing Policy#C1]" in resp.content
    assert resp.total_tokens > 0


@pytest.mark.asyncio
async def test_fallback_mechanism():
    # Calling with preferred provider that is not running (e.g. ollama) should fall back gracefully
    resp = await generate_with_fallback(
        prompt="What is the refund policy?",
        context={"retrieved_chunks": [{"citation_token": "[Doc:Refund Policy#C1]"}]},
        preferred_provider="ollama"
    )
    assert resp.fallback_used is True
    assert resp.provider_name == "mock"
