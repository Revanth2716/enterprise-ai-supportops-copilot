import React from 'react';
import { Shield, MessageSquare, BookOpen, CheckCircle, BarChart3, Cpu } from 'lucide-react';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  provider: string;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, provider }) => {
  return (
    <header className="header">
      <div className="header-brand">
        <Shield size={24} color="#3b82f6" />
        <span>Enterprise AI SupportOps Copilot</span>
        <span style={{ fontSize: '0.72rem', background: '#1e293b', color: '#38bdf8', padding: '2px 8px', borderRadius: '12px', border: '1px solid #334155' }}>
          2026 FLAGSHIP
        </span>
      </div>

      <nav className="nav-tabs">
        <button
          className={`nav-tab ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          <MessageSquare size={16} />
          Copilot Chat
        </button>
        <button
          className={`nav-tab ${activeTab === 'knowledge' ? 'active' : ''}`}
          onClick={() => setActiveTab('knowledge')}
        >
          <BookOpen size={16} />
          Knowledge Base
        </button>
        <button
          className={`nav-tab ${activeTab === 'evals' ? 'active' : ''}`}
          onClick={() => setActiveTab('evals')}
        >
          <CheckCircle size={16} />
          Benchmark Evals
        </button>
        <button
          className={`nav-tab ${activeTab === 'metrics' ? 'active' : ''}`}
          onClick={() => setActiveTab('metrics')}
        >
          <BarChart3 size={16} />
          Telemetry & Cost
        </button>
      </nav>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: '#10b981', background: 'rgba(16,185,129,0.1)', padding: '4px 10px', borderRadius: '12px', border: '1px solid rgba(16,185,129,0.2)' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }}></span>
          $0.00 Base Cost
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: '#94a3b8', background: '#121826', padding: '4px 10px', borderRadius: '12px', border: '1px solid #23304a' }}>
          <Cpu size={14} />
          {provider || 'MockProvider'}
        </div>
      </div>
    </header>
  );
};
