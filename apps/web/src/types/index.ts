export interface CitationItem {
  citation_token: string;
  document_title?: string;
  chunk_id?: string;
  content_excerpt?: string;
}

export interface ToolCallItem {
  tool_name: string;
  source: string;
  success: boolean;
  parameters: Record<string, any>;
  duration_ms: number;
  result_summary: string;
}

export interface ExecutionStepItem {
  step_order: number;
  step_name: string;
  status: 'SUCCESS' | 'WARNING' | 'ERROR' | 'BLOCKED';
  duration_ms: number;
  details: Record<string, any>;
}

export interface ChatMetrics {
  total_duration_ms: number;
  total_tokens: number;
  estimated_cost_usd: number;
  provider: string;
  model: string;
  fallback_used: boolean;
}

export interface ChatResponse {
  run_id: string;
  session_id: string;
  query: string;
  status: 'SUCCESS' | 'FAILED' | 'GUARD_BLOCKED';
  response: string;
  confidence_score: number;
  retrieval_mode: string;
  citations: CitationItem[];
  tool_calls: ToolCallItem[];
  execution_trace: ExecutionStepItem[];
  metrics: ChatMetrics;
}

export interface EvalCase {
  case_code: string;
  category: string;
  passed: boolean;
  duration_ms: number;
  is_blocked: boolean;
  reasons: string[];
}

export interface EvalScorecard {
  has_run: boolean;
  total_cases: number;
  passed_cases: number;
  retrieval_hit_rate: number;
  tool_accuracy: number;
  groundedness_score: number;
  safety_pass_rate: number;
  avg_latency_ms: number;
  details: EvalCase[];
}

export interface KnowledgeDocument {
  id: string;
  title: string;
  category: string;
  version: string;
  chunk_count: number;
}
