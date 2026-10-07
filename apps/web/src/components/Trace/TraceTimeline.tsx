import React from 'react';
import { ExecutionStepItem } from '../../types';
import { CheckCircle2, AlertTriangle, XCircle, Clock } from 'lucide-react';

interface TraceTimelineProps {
  steps: ExecutionStepItem[];
}

export const TraceTimeline: React.FC<TraceTimelineProps> = ({ steps }) => {
  if (!steps || steps.length === 0) {
    return <div style={{ color: '#64748b', fontSize: '0.85rem' }}>No active execution trace. Submit an inquiry to inspect the bounded agent state machine.</div>;
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return <CheckCircle2 size={16} color="#10b981" />;
      case 'WARNING':
        return <AlertTriangle size={16} color="#f59e0b" />;
      case 'BLOCKED':
      case 'ERROR':
        return <XCircle size={16} color="#ef4444" />;
      default:
        return <Clock size={16} color="#94a3b8" />;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {steps.map((s, idx) => (
        <div key={idx} className="trace-step">
          <div style={{ marginTop: '2px' }}>{getStatusIcon(s.status)}</div>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontWeight: 600, color: '#f1f5f9' }}>{s.step_name}</span>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontFamily: 'var(--font-mono)' }}>
                {s.duration_ms}ms
              </span>
            </div>
            {s.details && Object.keys(s.details).length > 0 && (
              <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginTop: '4px', background: '#121826', padding: '4px 8px', borderRadius: '4px', border: '1px solid #1a2234' }}>
                {Object.entries(s.details).map(([k, v]) => (
                  <span key={k} style={{ marginRight: '8px' }}>
                    <strong>{k}:</strong> {String(v)}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
