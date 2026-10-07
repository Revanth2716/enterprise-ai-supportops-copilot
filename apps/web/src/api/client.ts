import { ChatResponse, EvalScorecard, KnowledgeDocument } from '../types';

const API_BASE = '/api/v1';

export async function sendChatMessage(query: string, sessionId?: string): Promise<ChatResponse> {
  const resp = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, session_id: sessionId })
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: 'API call failed' }));
    throw new Error(err.detail || `Server error: ${resp.status}`);
  }
  return resp.json();
}

export async function fetchKnowledge(): Promise<{ total_documents: number; documents: KnowledgeDocument[] }> {
  const resp = await fetch(`${API_BASE}/knowledge`);
  if (!resp.ok) throw new Error('Failed to fetch knowledge');
  return resp.json();
}

export async function fetchEvaluations(): Promise<EvalScorecard> {
  const resp = await fetch(`${API_BASE}/evaluations`);
  if (!resp.ok) throw new Error('Failed to fetch evaluations');
  return resp.json();
}

export async function triggerEvaluations(): Promise<{ status: string; scorecard: EvalScorecard }> {
  const resp = await fetch(`${API_BASE}/evaluations/run`, { method: 'POST' });
  if (!resp.ok) throw new Error('Failed to run benchmark suite');
  return resp.json();
}

export async function fetchMetrics(): Promise<any> {
  const resp = await fetch(`${API_BASE}/metrics`);
  if (!resp.ok) throw new Error('Failed to fetch metrics');
  return resp.json();
}

export async function fetchHealth(): Promise<any> {
  const resp = await fetch('/health');
  if (!resp.ok) throw new Error('Failed to fetch health status');
  return resp.json();
}
