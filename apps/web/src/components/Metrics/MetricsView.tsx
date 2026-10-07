import React, { useState, useEffect } from 'react';
import { fetchMetrics } from '../../api/client';
import { BarChart3, Database, Coins, ShieldAlert, Cpu } from 'lucide-react';

export const MetricsView: React.FC = () => {
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    fetchMetrics().then(setMetrics).catch(console.error);
  }, []);

  return (
    <div style={{ flex: 1, padding: '32px', overflowY: 'auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '6px' }}>
          System Telemetry & Cost Accounting
        </h2>
        <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>
          Real-time operational accounting for LLM token usage, request latency, estimated cloud costs, and Prometheus instrumentation.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginBottom: '32px' }}>
        <div className="metric-card">
          <div className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Database size={16} color="#3b82f6" />
            Total Copilot Runs
          </div>
          <div className="metric-value">{metrics?.total_agent_runs || 0}</div>
        </div>

        <div className="metric-card">
          <div className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Cpu size={16} color="#8b5cf6" />
            Tokens Consumed
          </div>
          <div className="metric-value">{metrics?.total_tokens_consumed || 0}</div>
        </div>

        <div className="metric-card">
          <div className="metric-label" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Coins size={16} color="#10b981" />
            Accumulated Cost
          </div>
          <div className="metric-value" style={{ color: '#10b981' }}>
            ${metrics?.total_estimated_cost_usd?.toFixed(4) || '0.0000'}
          </div>
          <div style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '4px' }}>
            Zero-Cost Local Default Mode
          </div>
        </div>
      </div>

      <div className="inspector-card">
        <div className="inspector-title">
          <BarChart3 size={16} />
          Prometheus Observability Scraping
        </div>
        <p style={{ color: '#94a3b8', fontSize: '0.85rem', marginBottom: '12px' }}>
          Standard Prometheus metrics are exported via <code>GET /metrics</code> and ready for scraping by Prometheus or Grafana agent collectors.
        </p>
        <div style={{ background: '#0c111d', padding: '16px', borderRadius: '8px', border: '1px solid var(--border-color)', fontFamily: 'var(--font-mono)', fontSize: '0.82rem', color: '#cbd5e1' }}>
          <div># HELP supportops_requests_total Total requests processed by SupportOps Copilot</div>
          <div># TYPE supportops_requests_total counter</div>
          <div>supportops_requests_total&#123;status="success"&#125; {metrics?.total_agent_runs || 0}</div>
          <div style={{ marginTop: '8px' }}># HELP supportops_estimated_cost_usd_total Estimated total cost in USD</div>
          <div># TYPE supportops_estimated_cost_usd_total counter</div>
          <div>supportops_estimated_cost_usd_total 0.000000</div>
        </div>
      </div>
    </div>
  );
};
