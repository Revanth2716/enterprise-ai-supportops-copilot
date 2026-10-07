# Enterprise AI SupportOps Copilot

[![CI Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.12%20%7C%203.14-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)]()
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg)]()
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)]()
[![pgvector](https://img.shields.io/badge/Vector%20DB-pgvector-336791.svg)]()
[![FastEmbed](https://img.shields.io/badge/Embeddings-FastEmbed%20Local-purple.svg)]()
[![MCP](https://img.shields.io/badge/Protocol-MCP%20JSON--RPC-blueviolet.svg)]()
[![Cost](https://img.shields.io/badge/Base%20Cost-%240.00%20(Local%20%2F%20Mock)-success.svg)]()

> **Flagship 2026 AI Engineer Portfolio Project**: A production-grade, full-stack AI co-pilot designed for enterprise customer operations teams. Features bounded state machine agent orchestration, local hybrid RAG with pgvector and FastEmbed, Model Context Protocol (MCP) tool integration, multi-layered security guardrails, a restricted AST arithmetic evaluator, glass-box execution observability, and automated deterministic evaluation benchmarks.

---

## 1. Executive Summary & Problem Statement

In enterprise support operations (Tier-2 and Tier-3 technical support), frontline engineers face extreme cognitive load. When high-value customers (such as ACME Corp) report complex discrepancies—such as billing duplicate charges, contract disputes, or SLA breaches—support engineers must manually correlate disparate systems:
1. Static knowledge bases (Billing Policies, SLAs, Refund Guidelines)
2. Operational transactional databases (Customer CRM, Invoices, Orders, Payment Gateway Logs)
3. Incident management systems (Ticket drafts, escalations, audit logging)

Current generic LLM chatbots fail in enterprise environments because they:
- Hallucinate policies without grounding.
- Lack deterministic, safe access to operational databases.
- Expose raw, uninspected chain-of-thought to users.
- Fail to enforce strict PII, credential, and prompt injection guardrails.
- Cannot be evaluated quantitatively against ground-truth benchmarks.
- Require expensive cloud APIs for basic operations.

### The Solution
The **Enterprise AI SupportOps Copilot** acts as a secure co-pilot for support engineers. It ingests customer queries, validates them against multi-layered security guardrails, plans multi-step retrieval and tool invocations across hybrid knowledge bases and operational databases (via native registries and standard Model Context Protocol - MCP servers), validates citations against retrieved evidence, and generates grounded, enterprise-ready resolutions with complete operational observability.

---

## 2. High-Level System Architecture

```
                         ┌────────────────────────────────────────────────────────┐
                         │              React + TypeScript Frontend               │
                         │   (Chat, Run Trace, Evidence Drawer, Evals, Metrics)  │
                         └───────────────────────────┬────────────────────────────┘
                                                     │ HTTP / REST
                                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   FastAPI Application Gateway                                   │
│  ┌───────────────────────┐  ┌───────────────────────────┐  ┌─────────────────────────────────┐  │
│  │ Request ID Middleware │  │ Security & Input Guards   │  │  Structured Pydantic Models     │  │
│  │  (Tracing & Logging)  │  │ (Injection/PII/Secret/Len)│  │ (Strict Schema Input/Output)    │  │
│  └───────────────────────┘  └─────────────┬─────────────┘  └─────────────────────────────────┘  │
│                                           │                                                     │
│                                           ▼                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                             LangGraph Bounded State Orchestrator                          │  │
│  │       [START] ──► [Guard Check] ──► [Classify Intent] ──► [Hybrid RAG] ──► [Plan Tools]   │  │
│  │                                                                                  │        │  │
│  │       [END] ◄── [Output Guard] ◄── [Validate Citations] ◄── [Synthesize] ◄┼─── [Execute] │  │
│  └───────────────────────────┬───────────────────────────────────────────┬───────────────────┘  │
│                              │                                           │                      │
│                              ▼                                           ▼                      │
│  ┌─────────────────────────────────────────┐   ┌─────────────────────────────────────────────┐  │
│  │       Hybrid RAG Engine (Local)         │   │         Tool Registry & MCP Server          │  │
│  │  - FastEmbed 384-d Dense Semantic Vector│   │  - Customer Lookup (get_customer)           │  │
│  │  - PostgreSQL tsvector Lexical Search   │   │  - Order Inspector (get_order_history)      │  │
│  │  - Reciprocal Rank Fusion (RRF)         │   │  - Policy Lookup (lookup_policy)            │  │
│  │  - Truthful Lexical Fallback Mode       │   │  - Restricted AST Evaluator (calculate)     │  │
│  │  - Grounded Citation Enforcement        │   │  - Ticket Drafter (draft_ticket)            │  │
│  └─────────────────────────────────────────┘   └─────────────────────────────────────────────┘  │
│                              │                                           │                      │
│                              └─────────────────────┬─────────────────────┘                      │
│                                                    ▼                                            │
│  ┌───────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                AI Provider Abstraction Layer                              │  │
│  │       ┌───────────────────────┐   ┌───────────────────────┐   ┌────────────────────────┐  │  │
│  │       │  MockProvider (P0)    │   │  OllamaProvider (P1)  │   │ OpenAI-Compatible (P1) │  │  │
│  │       │ (Deterministic, $0.00)│   │ (Local DeepSeek/Llama)│   │ (vLLM / Open-Router)   │  │  │
│  │       └───────────────────────┘   └───────────────────────┘   └────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                             │
                      ┌──────────────────────┴──────────────────────┐
                      ▼                                             ▼
       ┌───────────────────────────────┐             ┌───────────────────────────────┐
       │   PostgreSQL 16 + pgvector    │             │           Redis 7             │
       │ - CRM (Customers, Orders)     │             │ - Ephemeral Session State     │
       │ - Knowledge Docs & Embeddings │             │ - Idempotency Keys            │
       │ - Agent Runs, Steps, Traces   │             │ - Rate Limiting & Tool Cache  │
       │ - Eval Cases & Benchmark Runs │             │ - Graceful In-Memory Fallback │
       └───────────────────────────────┘             └───────────────────────────────┘
```

---

## 3. Visual Application Tour

Real production screenshots captured from the verified live stack:

| Copilot Chat & Quick Chips | Live Execution Trace & Evidence Drawer |
|:---:|:---:|
| ![Main Copilot Interface](docs/screenshots/01_main_copilot.png) | ![Trace and Evidence](docs/screenshots/02_trace_and_evidence.png) |

| Automated Benchmark Evaluations (15 Scenarios) | System Telemetry & Prometheus Metrics |
|:---:|:---:|
| ![Benchmark Evals Dashboard](docs/screenshots/03_evals_dashboard.png) | ![Telemetry and Cost](docs/screenshots/04_metrics_dashboard.png) |

| Real-Time Security Guardrail Intervention |
|:---:|
| ![Security Guardrail Intervention](docs/screenshots/05_security_guard_blocked.png) |

---

## 4. Core AI Engineering Features

### 1. Local Hybrid RAG with FastEmbed & PostgreSQL pgvector
- **Primary Embedding Strategy**: FastEmbed running `sentence-transformers/all-MiniLM-L6-v2` locally on CPU using ONNX Runtime. Generates normalized 384-dimensional dense semantic vectors at **$0.00 API cost**.
- **Vector Persistence**: Vectors are indexed in PostgreSQL using `pgvector` with cosine distance (`<=>`).
- **Lexical Search & Reciprocal Rank Fusion (RRF)**: Concurrently runs full-text keyword matching (`tsvector` / `tsquery`) to ensure invoice identifiers (e.g., `INV-1042`) and specific clauses are never missed. Scores are fused via:
  $$\text{RRF\_Score}(d) = \frac{1}{60 + \text{rank}_{\text{semantic}}(d)} + \frac{1}{60 + \text{rank}_{\text{lexical}}(d)}$$
- **Truthful Lexical Fallback**: If FastEmbed cannot be initialized within the environment, the engine transparently degrades to pure lexical search (`tsvector`), logging `retrieval_mode="lexical_fallback"`. It **never claims semantic retrieval** or fabricates pseudo-vectors when operating in fallback mode.

### 2. Bounded State Machine Agent Orchestration (LangGraph)
- **Deterministic Workflow**: Replaces unpredictable autonomous agent loops with an explicit state graph:
  `guard_check` &rarr; `classify_intent` &rarr; `retrieve_knowledge` &rarr; `plan_tools` &rarr; `execute_tools` &rarr; `synthesize_response` &rarr; `validate_citations` &rarr; `output_guard`.
- **Hard Bounds**: Strict recursion limit (`<= 5`) and 15-second total execution timeout prevent runaway execution.
- **Glass-Box Operational Trace**: Replaces hidden chain-of-thought with structured operational step traces (e.g., `"Retrieved 2 billing chunks"`, `"Executed get_order_history"`).

### 3. Model Context Protocol (MCP) Integration
- Implements a standalone MCP server (`apps/mcp_server/server.py`) exposing safe enterprise tools (`search_knowledge`, `get_customer`, `get_order_history`, `lookup_policy`) over standard JSON-RPC 2.0.
- Includes an internal MCP client adapter with seamless local in-process fallback.

### 4. Restricted AST Arithmetic Evaluator
- To prevent code injection, arbitrary execution, and `ast.literal_eval` syntax errors on expressions like `149 * 2 - 149`:
  - **Permitted AST Nodes**: Numeric constants, binary operators (`+`, `-`, `*`, `/`, `%`, `**`), and unary operators (`+`, `-`).
  - **Rejected Syntax**: Variables (`ast.Name`), attribute access (`ast.Attribute`), function calls (`ast.Call`), imports, and subscripts.
  - **DoS Guards**: Expression length &le; 100 characters; exponents &le; 10; magnitude bounds &le; $10^{12}$; zero-division protection.
  - Zero `eval()` or `exec()`.

### 5. Multi-Layered Defense-in-Depth Guardrails
- **Pre-Agent Input Guard**: Scans for prompt injection signatures (`ignore previous instructions`, `system prompt override`, `developer mode`), redacts API credentials/tokens, masks customer SSNs and credit cards, and enforces a 2,000 character limit.
- **Tool-Level Guard**: Enforces explicit tool allowlists with strict Pydantic parameter validation and read-only least privilege.
- **Output Guard & Citation Verifier**: Scans output for system leakage and cross-references citation tokens (`[Doc:Billing#C1]`) against chunks actually retrieved in that session.

### 6. Quantitative Evaluation Benchmark Harness
- Built-in benchmark suite of **15 synthetic enterprise test cases** across billing disputes, refund policies, SLA breaches, and injection attacks.
- Quantitative metrics computed on every run:
  - **Retrieval Hit@3**: &ge; 90%
  - **Tool Call Accuracy**: &ge; 95%
  - **Answer Groundedness**: &ge; 90%
  - **Safety Pass Rate**: 100.0%
- Accessible via CLI (`python -m evals.runner.evaluator`), REST API (`POST /api/v1/evaluations/run`), and the React Dashboard.

### 7. Observability, Prometheus Metrics & Cost Accounting
- Every request is tagged with an `X-Request-ID` and logged in structured JSON.
- Real-time Prometheus metrics exported at `/metrics`:
  - `supportops_requests_total`
  - `supportops_request_duration_seconds`
  - `supportops_tool_calls_total`
  - `supportops_llm_tokens_total`
  - `supportops_estimated_cost_usd_total` ($0.00 for mock/local)
  - `supportops_guardrail_blocks_total`

---

## 5. End-to-End Demo Scenario: The ACME Duplicate Charge

### Inquiry:
> *"Customer ACME says their invoice INV-1042 was charged twice. Find the relevant billing policy, inspect their recent orders, identify the likely cause, and draft a response."*

### Execution Lifecycle:
1. **Security Guard**: Input length: 138 chars. Injection score: 0.0. PII: None. &rarr; **PASSED**.
2. **Intent Classification**: Intent: `billing_dispute`. Entities: `Customer="ACME Corporation"`, `Invoice="INV-1042"`.
3. **Hybrid RAG**: Queries pgvector + tsvector on billing policy. Retrieves `Billing Policy 2026`, Section 3: Duplicate Charge Resolution (`[Doc:Enterprise Global Billing Policy (2026 Edition)#C1]`).
4. **Tool Execution**:
   - `get_customer(customer_identifier="ACME")` &rarr; Account `ACC-ACME-901`, Tier: `Enterprise`.
   - `get_order_history(customer_id="CUST-001", invoice_number="INV-1042")` &rarr; Identifies 2 charges of `$149.00` on 2026-10-01 (`TXN-88102-PRIMARY` and `TXN-88103-RETRY`).
   - `calculate("149.00 * 2 - 149.00")` &rarr; Reversal amount: `$149.00`.
   - `draft_ticket(customer_id="CUST-001", title="Duplicate Charge Adjustment INV-1042")` &rarr; Formats resolution draft.
5. **Grounded Synthesis**: Formulates grounded resolution with inline citation.
6. **Citation Validation**: Verifies `[Doc:Enterprise Global Billing Policy (2026 Edition)#C1]` exists in retrieved chunks. &rarr; **PASSED**.
7. **Inspector View**: UI displays grounded response, live trace timeline (all green), citation cards, and metrics (`~140ms | 505 tokens | $0.00 cost`).

---

## 6. Quickstart & Local Installation

### Prerequisites
- Python 3.12+ (or 3.14)
- Node.js 20+
- (Optional) Docker & Docker Compose

### Option A: Local Development Setup (Fastest)

```bash
# 1. Clone repository
git clone https://github.com/your-username/enterprise-ai-supportops-copilot.git
cd enterprise-ai-supportops-copilot

# 2. Setup Backend
cd apps/api
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Seed Database with Synthetic Data
python -m db.seed.seed_data

# 4. Start FastAPI Backend (Port 8000)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 5. In a new terminal, Start Frontend (Port 3000)
cd ../web
npm install
npm run dev
```

Open your browser at `http://localhost:3000`.

### Option B: Docker Compose (Single Command)

```bash
docker compose -f infra/docker-compose.yml up --build
```
Services started:
- `api` &rarr; `http://localhost:8000`
- `web` &rarr; `http://localhost:3000`
- `postgres` &rarr; `localhost:5432` (with pgvector)
- `redis` &rarr; `localhost:6379`
- `mcp-server` &rarr; `localhost:8001`

---

## 7. Verification & Automated Test Suite

Run the full automated test suite covering security guardrails, tools, restricted AST evaluation, RAG hybrid retrieval, agent state machine, and evaluation benchmarks:

```bash
# Run pytest with coverage
pytest apps/api/tests -v --cov=app

# Run evaluation benchmark CLI runner
python -m evals.runner.evaluator
```

---

## 8. 2026 AI Engineer Portfolio Talking Points

1. **Why Bounded LangGraph instead of an Autonomous Swarm?**  
   Autonomous swarms lack SLA predictability and are prone to infinite loops and hallucinations. In enterprise support operations, a bounded state machine with explicit typed state and single-pass tool planning provides auditability and deterministic execution bounds.
2. **How is Answer Grounding Guaranteed?**  
   Every retrieved chunk receives a deterministic citation token. The state graph contains an automated Citation Verification node that cross-references output tokens against retrieved chunks before releasing the response.
3. **How does the Tool Architecture Prevent Code/SQL Injection?**  
   The LLM never generates raw SQL or executable code. Tools are deterministic wrappers with strict Pydantic schemas. The arithmetic calculator uses a custom restricted AST visitor that strictly allowlists arithmetic nodes and rejects variable names, attributes, function calls, and imports. Selected tools are also exposed via standard Model Context Protocol (MCP).
4. **How are Costs and Privacy Handled?**  
   The application runs locally at **$0.00 cost** via our `MockProvider` and local CPU FastEmbed vectors. All customer datasets are 100% synthetic, and Prometheus observability accounts for every token and latency millisecond.

---

## 9. License

Distributed under the MIT License. See `LICENSE` for more information.
