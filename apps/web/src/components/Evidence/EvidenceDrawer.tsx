import React from 'react';
import { CitationItem, ToolCallItem } from '../../types';
import { BookOpen, Wrench, Check } from 'lucide-react';

interface EvidenceDrawerProps {
  citations: CitationItem[];
  toolCalls: ToolCallItem[];
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({ citations, toolCalls }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Citations Section */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', fontWeight: 600, color: '#38bdf8', marginBottom: '8px' }}>
          <BookOpen size={14} />
          VERIFIED KNOWLEDGE CITATIONS ({citations?.length || 0})
        </div>
        {citations && citations.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {citations.map((c, i) => (
              <div key={i} style={{ background: '#121826', padding: '10px', borderRadius: '6px', border: '1px solid #23304a', fontSize: '0.82rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span className="citation-chip">{c.citation_token}</span>
                  <span style={{ fontSize: '0.72rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Check size={12} /> Verified Chunk
                  </span>
                </div>
                {c.document_title && <div style={{ fontWeight: 600, color: '#e2e8f0', marginBottom: '2px' }}>{c.document_title}</div>}
                {c.content_excerpt && <div style={{ color: '#94a3b8', fontStyle: 'italic', fontSize: '0.78rem' }}>"{c.content_excerpt}"</div>}
              </div>
            ))}
          </div>
        ) : (
          <div style={{ color: '#64748b', fontSize: '0.8rem' }}>No citation tokens required for this inquiry.</div>
        )}
      </div>

      {/* Tool Calls Section */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', fontWeight: 600, color: '#a78bfa', marginBottom: '8px' }}>
          <Wrench size={14} />
          OPERATIONAL TOOL CALLS ({toolCalls?.length || 0})
        </div>
        {toolCalls && toolCalls.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {toolCalls.map((t, idx) => (
              <div key={idx} style={{ background: '#121826', padding: '10px', borderRadius: '6px', border: '1px solid #23304a', fontSize: '0.82rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 600, color: '#f1f5f9' }}>{t.tool_name}</span>
                  <span style={{ fontSize: '0.72rem', color: '#94a3b8', background: '#1a2234', padding: '2px 6px', borderRadius: '4px' }}>
                    {t.source.toUpperCase()} ({t.duration_ms}ms)
                  </span>
                </div>
                <div style={{ color: '#94a3b8', fontSize: '0.76rem', fontFamily: 'var(--font-mono)', wordBreak: 'break-all' }}>
                  {t.result_summary}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ color: '#64748b', fontSize: '0.8rem' }}>No tools invoked.</div>
        )}
      </div>
    </div>
  );
};
