import asyncio
import time
from typing import Dict, Any, Optional
from app.ai.base import AIProvider, ProviderResponse


class MockProvider(AIProvider):
    """
    Zero-Cost ($0.00), Deterministic, Offline AI Provider.
    Inspects gathered evidence (retrieved chunks and tool results)
    to synthesize grounded, cited responses.
    """

    def __init__(self, model_name: str = "supportops-mock-v1"):
        super().__init__(name="mock", model_name=model_name)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ProviderResponse:
        start_time = time.perf_counter()

        # Simulate brief realistic async execution latency
        await asyncio.sleep(0.08)

        context = context or {}
        chunks = context.get("retrieved_chunks", [])
        tool_results = context.get("tool_results", {})

        # Find primary citation token if available
        primary_citation = chunks[0].get("citation_token", "[Doc:Enterprise Global Billing Policy (2026 Edition)#C1]") if chunks else "[Doc:Billing Policy#C1]"

        # Check for duplicate billing dispute
        has_dup = False
        orders_data = tool_results.get("get_order_history", {})
        if isinstance(orders_data, dict) and orders_data.get("has_duplicate_charges"):
            has_dup = True

        cust_data = tool_results.get("get_customer", {})
        cust_name = cust_data.get("name", "ACME Corporation") if isinstance(cust_data, dict) else "Customer"

        if has_dup or "1042" in prompt or "duplicate" in prompt.lower():
            content = (
                f"Customer {cust_name} experienced an automated duplicate charge for invoice INV-1042 "
                f"($149.00 billed twice on 2026-10-01) due to a payment gateway retry anomaly. "
                f"Under official company policy {primary_citation}, duplicate charges within a 48-hour window "
                f"are classified as erroneous deductions and are authorized for an immediate credit reversal "
                f"without requiring secondary managerial sign-off. "
                f"A formal support resolution draft has been prepared with a $149.00 refund adjustment."
            )
        elif "refund" in prompt.lower() or "cancel" in prompt.lower():
            refund_citation = chunks[0].get("citation_token", "[Doc:Enterprise Refund & Credit Adjustment Policy#C1]") if chunks else "[Doc:Refund Policy#C1]"
            content = (
                f"According to company guidelines {refund_citation}, enterprise accounts are eligible for full refunds "
                f"within 30 days of contract renewal if core service capabilities do not meet agreed technical specifications. "
                f"Erroneous deductions are 100% refundable immediately to the original payment instrument within 3 to 5 business days."
            )
        elif "sla" in prompt.lower() or "uptime" in prompt.lower():
            sla_citation = chunks[0].get("citation_token", "[Doc:Enterprise Service Level Agreement (SLA) Guidelines#C1]") if chunks else "[Doc:SLA Guidelines#C1]"
            content = (
                f"Under the enterprise agreement {sla_citation}, we provide a 99.95% monthly uptime guarantee for Enterprise tier customers. "
                f"For critical P1 incidents, our initial response window is guaranteed within 15 minutes, with remedies of 10% to 50% "
                f"service credits for validated uptime breaches."
            )
        else:
            content = (
                f"Based on our enterprise operating procedures {primary_citation}, customer account inquiry for {cust_name} "
                f"has been verified against current operational records. All procedures have been validated against our knowledge base."
            )

        prompt_tokens = len(prompt.split()) + 180
        completion_tokens = len(content.split())
        total_tokens = prompt_tokens + completion_tokens
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        return ProviderResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=elapsed_ms,
            estimated_cost_usd=0.000000,  # Always $0.00 for local mock
            provider_name=self.name,
            model_name=self.model_name,
            fallback_used=False
        )
