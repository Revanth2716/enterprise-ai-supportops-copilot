import React, { useState, useEffect } from 'react';
import { Header } from './components/Layout/Header';
import { ChatView } from './components/Chat/ChatView';
import { EvalsDashboard } from './components/Evals/EvalsDashboard';
import { MetricsView } from './components/Metrics/MetricsView';
import { fetchHealth, fetchKnowledge } from './api/client';
import { KnowledgeDocument } from './types';
import { BookOpen, FileCheck } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'knowledge' | 'evals' | 'metrics'>('chat');
  const [provider, setProvider] = useState('MockProvider');
  const [knowledgeDocs, setKnowledgeDocs] = useState<KnowledgeDocument[]>([]);

  useEffect(() => {
    fetchHealth()
      .then(h => {
        if (h.provider) setProvider(h.provider === 'mock' ? 'MockProvider' : h.provider);
      })
      .catch(() => {});

    fetchKnowledge()
      .then(k => setKnowledgeDocs(k.documents || []))
      .catch(() => {});
  }, []);

  return (
    <div className="app-container">
      <Header activeTab={activeTab} setActiveTab={setActiveTab as any} provider={provider} />

      <main className="main-content">
        {activeTab === 'chat' && <ChatView />}

        {activeTab === 'knowledge' && (
          <div style={{ flex: 1, padding: '32px', overflowY: 'auto' }}>
            <div style={{ marginBottom: '24px' }}>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '6px' }}>
                Enterprise Knowledge Repository
              </h2>
              <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>
                Operational policies and standard operating procedures chunked and indexed with pgvector for hybrid retrieval.
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
              {knowledgeDocs.map(doc => (
                <div key={doc.id} className="inspector-card">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: '#38bdf8', fontWeight: 600 }}>
                    <BookOpen size={16} />
                    {doc.title}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '12px' }}>
                    Category: <strong style={{ color: '#e2e8f0' }}>{doc.category}</strong> | Version: {doc.version}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: '#10b981', background: 'rgba(16,185,129,0.1)', padding: '4px 8px', borderRadius: '4px', width: 'fit-content' }}>
                    <FileCheck size={14} />
                    {doc.chunk_count || 4} chunks indexed
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'evals' && <EvalsDashboard />}
        {activeTab === 'metrics' && <MetricsView />}
      </main>
    </div>
  );
};

export default App;
