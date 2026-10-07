from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Metrics definitions
REQUESTS_TOTAL = Counter(
    "supportops_requests_total",
    "Total requests processed by SupportOps Copilot",
    ["status"]
)

REQUEST_DURATION_SECONDS = Histogram(
    "supportops_request_duration_seconds",
    "Latency of SupportOps Copilot requests",
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

TOOL_CALLS_TOTAL = Counter(
    "supportops_tool_calls_total",
    "Total tool calls executed",
    ["tool", "success"]
)

LLM_TOKENS_TOTAL = Counter(
    "supportops_llm_tokens_total",
    "Total LLM tokens tracked",
    ["type", "provider"]
)

ESTIMATED_COST_USD_TOTAL = Counter(
    "supportops_estimated_cost_usd_total",
    "Estimated total cost in USD for LLM usage"
)

GUARDRAIL_BLOCKS_TOTAL = Counter(
    "supportops_guardrail_blocks_total",
    "Total requests blocked by security guardrails",
    ["reason"]
)


def get_prometheus_metrics() -> bytes:
    return generate_latest()
