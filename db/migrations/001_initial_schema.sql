-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Users / Operators
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'support_engineer',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Enterprise Customers
CREATE TABLE IF NOT EXISTS customers (
    id VARCHAR(36) PRIMARY KEY,
    account_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    tier VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    support_pin VARCHAR(20),
    primary_contact VARCHAR(150),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Invoices & Orders (Transactional Data)
CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    invoice_number VARCHAR(50) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'USD',
    status VARCHAR(50) NOT NULL,
    line_items JSONB NOT NULL DEFAULT '[]'::jsonb,
    transaction_reference VARCHAR(100),
    notes TEXT,
    billing_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_orders_customer_invoice ON orders(customer_id, invoice_number);

-- 4. Support Tickets
CREATE TABLE IF NOT EXISTS tickets (
    id VARCHAR(36) PRIMARY KEY,
    ticket_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id VARCHAR(36) NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    drafted_response TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Knowledge Documents & Chunks
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    version VARCHAR(20) NOT NULL DEFAULT '1.0',
    content_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id VARCHAR(36) PRIMARY KEY,
    document_id VARCHAR(36) NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    tsv_content TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    embedding VECTOR(384) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_chunks_tsv ON document_chunks USING GIN(tsv_content);

-- 6. Agent Execution Runs
CREATE TABLE IF NOT EXISTS agent_runs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id),
    session_id VARCHAR(64) NOT NULL,
    user_query TEXT NOT NULL,
    sanitized_query TEXT NOT NULL,
    status VARCHAR(50) NOT NULL,
    final_response TEXT,
    confidence_score NUMERIC(4, 3),
    total_duration_ms INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    estimated_cost_usd NUMERIC(8, 6) NOT NULL DEFAULT 0.000000,
    provider_used VARCHAR(50) NOT NULL,
    fallback_occurred BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_agent_runs_session ON agent_runs(session_id);

-- 7. Operational Step Trace
CREATE TABLE IF NOT EXISTS agent_steps (
    id VARCHAR(36) PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    duration_ms INTEGER NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_agent_steps_run ON agent_steps(run_id, step_order);

-- 8. Tool Call Logs
CREATE TABLE IF NOT EXISTS tool_calls (
    id VARCHAR(36) PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
    tool_name VARCHAR(100) NOT NULL,
    source VARCHAR(20) NOT NULL DEFAULT 'local',
    input_parameters JSONB NOT NULL,
    output_result JSONB NOT NULL,
    duration_ms INTEGER NOT NULL,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. LLM Operational Ledger
CREATE TABLE IF NOT EXISTS llm_calls (
    id VARCHAR(36) PRIMARY KEY,
    run_id VARCHAR(36) REFERENCES agent_runs(id) ON DELETE SET NULL,
    provider VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    prompt_tokens INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    latency_ms INTEGER NOT NULL,
    estimated_cost_usd NUMERIC(8, 6) NOT NULL DEFAULT 0.000000,
    status VARCHAR(50) NOT NULL,
    fallback_used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. Evaluation Benchmark Cases & Results
CREATE TABLE IF NOT EXISTS evaluation_cases (
    id VARCHAR(36) PRIMARY KEY,
    case_code VARCHAR(50) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL,
    query TEXT NOT NULL,
    expected_tools JSONB NOT NULL,
    expected_citations JSONB NOT NULL,
    ground_truth_assertion TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evaluation_runs (
    id VARCHAR(36) PRIMARY KEY,
    run_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    total_cases INTEGER NOT NULL,
    passed_cases INTEGER NOT NULL,
    retrieval_hit_rate NUMERIC(5, 4) NOT NULL,
    tool_accuracy NUMERIC(5, 4) NOT NULL,
    groundedness_score NUMERIC(5, 4) NOT NULL,
    safety_pass_rate NUMERIC(5, 4) NOT NULL,
    avg_latency_ms INTEGER NOT NULL,
    details JSONB NOT NULL DEFAULT '[]'::jsonb
);
