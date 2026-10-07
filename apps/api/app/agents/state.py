from typing import TypedDict, List, Dict, Any, Optional


class StepTrace(TypedDict):
    step_order: int
    step_name: str
    status: str  # SUCCESS, WARNING, ERROR, BLOCKED
    duration_ms: int
    details: Dict[str, Any]


class AgentState(TypedDict):
    session_id: str
    user_id: Optional[str]
    raw_query: str
    sanitized_query: str
    is_blocked: bool
    block_reasons: List[str]
    intent: str
    entities: Dict[str, Any]
    required_tools: List[Dict[str, Any]]
    retrieved_chunks: List[Dict[str, Any]]
    retrieval_mode: str
    tool_results: Dict[str, Any]
    tool_calls_trace: List[Dict[str, Any]]
    synthesized_response: str
    validated_citations: List[Dict[str, Any]]
    unverified_citations: List[str]
    confidence_score: float
    provider_used: str
    model_name: str
    fallback_used: bool
    total_tokens: int
    estimated_cost_usd: float
    execution_steps: List[StepTrace]
    recursion_count: int
    error: Optional[str]
