# AgentTrust System Architecture

## 1. Overview

**AgentTrust** is an independent reliability evaluation platform for AI agents. Rather than treating evaluation as an opaque LLM prompt that outputs a subjective score, AgentTrust treats evaluation as an observable, multi-layered diagnostic pipeline that evaluates an agent's factual correctness, evidence grounding, citation validity, cross-lingual translation fidelity, and trajectory integrity.

---

## 2. High-Level Architecture Diagram

```mermaid
graph TD
    UI[Next.js + Tailwind Dashboard] -->|REST / OpenAPI| API[FastAPI Backend]
    
    subgraph Data & Storage
        DB[(PostgreSQL / SQLite)]
        DOCS[Statutory Document Store]
        TESTS[Structured Test Suites]
    end
    
    subgraph Execution & Evaluation
        Runner[Evaluation Runner]
        Adapter[Agent Adapter Layer]
        Orchestrator[Evaluation Orchestrator]
    end
    
    subgraph Agents Under Test
        DemoAgent[Demo Agent (Simulated RAG)]
        HTTPAgent[External HTTP Agent POST /run]
    end
    
    subgraph Evaluator Subsystem
        Corr[Correctness Evaluator]
        Ground[Grounding Evaluator]
        Cite[Citation Evaluator]
        Trans[Translation Fidelity Evaluator]
        Traj[Trajectory Evaluator]
        Metrics[Metrics Engine]
    end
    
    API --> Runner
    Runner --> TESTS
    Runner --> Adapter
    Adapter --> DemoAgent
    Adapter --> HTTPAgent
    DemoAgent --> DOCS
    Runner --> Orchestrator
    Orchestrator --> Corr
    Orchestrator --> Ground
    Orchestrator --> Cite
    Orchestrator --> Trans
    Orchestrator --> Traj
    Orchestrator --> Metrics
    Runner --> DB
    API --> DB
```

---

## 3. Core Components

### 3.1 Agent Adapter Layer (`app/agents/`)
AgentTrust is decoupled from the agent under test.
- **`BaseAgentAdapter`**: Standard interface `run(test_case) -> AgentRunResult`.
- **`DemoAgentAdapter`**: Built-in RAG agent with configurable failure simulation modes (e.g. wrong fact rate, citation error rate, translation drift, missing retrieval).
- **`HTTPAgentAdapter`**: Connects any external AI agent via HTTP REST endpoint (`POST {endpoint}`).

### 3.2 Observable Trace Logging (`app/models/trace.py`)
Only observable agent interactions are recorded:
- `agent_start`
- `retrieval`
- `tool_call`
- `tool_result`
- `generation`
- `translation`
- `agent_end`
Hidden chain-of-thought is never inspected or relied upon.

### 3.3 Evaluation Engine (`app/evaluator/`)
- **Correctness**: Layer A (deterministic extraction of dates, section IDs, authorities) + Layer B (LLM semantic judge).
- **Grounding**: Claims cross-referenced against retrieved documents: `SUPPORTED`, `UNSUPPORTED`, `CONTRADICTED`.
- **Citation**: Validates source existence, section existence, and evidence correspondence.
- **Translation Fidelity**: Multilingual back-translation semantic preservation across English, Kannada, Hindi, and Telugu.
- **Trajectory Integrity**: Validates tool sequence, absence of redundant loops, and execution completion.

### 3.4 Metrics Engine (`app/evaluator/metrics.py`)
Computes aggregate rates, language breakdowns, and before/after run comparison deltas.
