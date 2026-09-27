# AgentTrust System Architecture
## Multilingual AI Reliability Evaluator

> **Tagline:** Evidence-backed reliability diagnostics for AI agents.

AgentTrust is an independent evaluation platform for AI agents. Rather than treating evaluation as an opaque LLM prompt that outputs a subjective trust score, AgentTrust treats evaluation as an observable, multi-layered diagnostic pipeline that evaluates an agent's factual correctness, evidence grounding, citation validity, cross-lingual translation fidelity, and observable trajectory integrity.

---

## 1. High-Level Architecture Diagram

```mermaid
graph TD
    subgraph Client Tier [Client Tier - Next.js 14 App Router]
        UI[AgentTrust Web Console]
        AuthUI[Auth: Login / Register / Workspace]
        DashboardUI[Overview & KPI Scorecards]
        RunsUI[Evaluation Runs & Pre-Flight Checks]
        DatasetsUI[Dataset Manager & Validation]
        AgentsUI[Agent Directory & Connection Probes]
        CompareUI[Before / After Run Comparisons]
        DrilldownUI[Failure Drill-down & Evidence Highlight]
    end

    subgraph APITier [API Tier - FastAPI Backend]
        AuthRouter[/api/auth - JWT & Sessions]
        WorkspaceRouter[/api/workspaces - Multi-Tenant Isolation]
        AgentRouter[/api/agents - Agent Registry & Probes]
        DatasetRouter[/api/datasets - Versioning & Validation]
        RunRouter[/api/runs - Preflight & Runner Execution]
        CompareRouter[/api/runs/compare & /regression]
        ReportRouter[/api/reports - HTML, CSV, JSON Exports]
    end

    subgraph SecurityStorage [Storage & Security Tier]
        DB[(PostgreSQL / SQLite with SQLAlchemy 2.0 Async)]
        AuditStore[(Audit Logs & Event Tracking)]
        EvidenceStore[(Corpus Documents & Chunks)]
    end

    subgraph ExecutionEngine [Execution & Adapter Tier]
        PreFlight[Pre-Flight Verification Engine]
        Runner[Evaluation Runner with Concurrency Semaphore]
        HTTPAdapter[HTTP Agent Adapter POST /run]
        SDKAdapter[Python SDK Adapter AgentTrustAdapter]
        DemoAdapter[Controlled Demo Simulation Agent]
    end

    subgraph EvaluatorSubsystem [Evaluator Subsystem]
        CorrEval[Hybrid Correctness Engine: Deterministic + Semantic]
        GroundEval[Grounding Engine: SUPPORTED / UNSUPPORTED / CONTRADICTED]
        CiteEval[Citation Engine: Existence, Section & Claim Correspondence]
        TransEval[Multilingual Translation Engine: Back-Translation Fidelity]
        TrajEval[Trajectory Integrity: Tool Sequence & Loop Detection]
        MetricsEngine[Dynamic Metrics & Composite Score Calculator]
        RegressionEngine[Automated Version Regression Analyzer]
    end

    UI --> APITier
    APITier --> SecurityStorage
    RunRouter --> PreFlight
    PreFlight --> Runner
    Runner --> HTTPAdapter
    Runner --> SDKAdapter
    Runner --> DemoAdapter
    Runner --> EvaluatorSubsystem
    EvaluatorSubsystem --> DB
    ReportRouter --> DB
```

---

## 2. Architectural Subsystems

### 2.1 Multi-Tenant User & Workspace Model
AgentTrust isolates all data under a structured hierarchical model:
```
User
  └── Workspace (Owner / Member / Admin)
        └── Projects
              ├── Registered Agents
              ├── Benchmark Datasets (Versioned: 1.0.0, 1.1.0)
              ├── Evaluation Profiles
              └── Evaluation Runs (Historical, Immutable)
```
- **Authentication**: Passwords hashed using `bcrypt`. State authenticated via signed JWT bearer tokens (`HS256`).
- **Authorization**: API dependencies verify workspace membership before reading or writing projects, agents, datasets, or runs.
- **Audit Logging**: Sensitive actions (logins, project creation, agent registration, runs launched, settings updated) are appended to `audit_logs` without capturing secrets.

### 2.2 Agent Adapter Tier & Protocols
AgentTrust does not require agents to run on internal infrastructure. Agents connect through two decoupled interfaces:

#### 1. HTTP Agent Adapter (`HTTPAgentAdapter`)
- External agent exposes a REST endpoint (e.g. `POST https://agent.enterprise.com/run`).
- AgentTrust transmits:
  ```json
  {
    "question": "What is the statutory deadline for filing an RTI appeal?",
    "language": "kn",
    "test_case_id": "KN-001"
  }
  ```
- Agent responds with the standard response schema:
  ```json
  {
    "answer": "ಮೇಲ್ಮನವಿ ಸಲ್ಲಿಸಲು ಕಾಲಮಿತಿ 30 ದಿನಗಳು.",
    "language": "kn",
    "citations": [
      { "document_id": "RTI_ACT_2005", "section": "Section 19(1)", "text": "within thirty days" }
    ],
    "retrieved_documents": [
      { "document_id": "RTI_ACT_2005", "chunk_id": "chunk_4", "text": "..." }
    ],
    "trace": [
      { "step": 1, "type": "retrieval", "tool": "document_search", "input": "..." },
      { "step": 2, "type": "tool_call", "protocol": "mcp", "tool": "calc_deadline" }
    ]
  }
  ```
- If citations, retrieved documents, or traces are omitted, AgentTrust records **"Not provided by agent"** rather than fabricating evidence.
- Connection Probing: `POST /api/agents/{id}/test-connection` verifies endpoint latency, response format, and schema compliance before starting evaluations.

#### 2. Python SDK Adapter (`sdk/agenttrust/`)
Allows in-process or local agent testing without exposing an HTTP endpoint:
```python
from sdk.agenttrust import AgentTrustAdapter, AgentRequest, AgentResponse

class EnterpriseRagAgent(AgentTrustAdapter):
    async def run(self, request: AgentRequest) -> AgentResponse:
        result = await my_rag_pipeline(request.question, lang=request.language)
        return AgentResponse(
            answer=result["text"],
            language=request.language,
            citations=result["citations"],
            trace=result["trace"]
        )
```

---

## 3. Evaluator Pipeline & Methodology

AgentTrust follows a strict evidence-based methodology:

```
Agent Execution Output
    │
    ├──> 1. Correctness Engine (Hybrid)
    │      ├── Deterministic Fact Matching (dates, numbers, sections, authorities)
    │      └── Semantic Judge (Structured JSON validation via LLM)
    │
    ├──> 2. Evidence Grounding Engine
    │      ├── Meaningful Claim Extraction
    │      ├── Candidate Evidence Lookup
    │      └── Classification: SUPPORTED | UNSUPPORTED | CONTRADICTED
    │
    ├──> 3. Citation Verification Engine
    │      ├── Source Existence Check
    │      ├── Referenced Section Check
    │      └── Evidence Correspondence & Claim Support Check
    │
    ├──> 4. Translation Fidelity Engine
    │      ├── Cross-Lingual Back-Translation to English
    │      ├── Numerical & Named Entity Preservation Check
    │      └── Classification: PASS | MINOR_DRIFT | MAJOR_DRIFT | FAIL
    │
    └──> 5. Observable Trajectory Engine
           ├── Required Retrieval & Tool Execution Verification
           ├── Repetitive Loop & Inefficient Call Detection
           └── MCP-Compatible Tool Trace Inspection
```

### 3.1 Composite Reliability Formula
$$\text{Composite Score} = 0.30 \times C_{\text{corr}} + 0.30 \times G_{\text{ground}} + 0.15 \times C_{\text{cite}} + 0.15 \times T_{\text{trans}} + 0.10 \times T_{\text{traj}}$$

*When translation is not applicable (e.g. English-only test cases), weights are normalized dynamically without penalizing the system.*

### 3.2 Failure Severity Rubric
- **CRITICAL**: Direct contradiction of verified facts, major numerical/statutory deadline error, or severe translation drift reversing meaning.
- **HIGH**: Substantial unsupported factual claim, incorrect cited section, or significant translation distortion.
- **MEDIUM**: Minor unsupported peripheral claim, formatting citation problem, or trajectory inefficiency.
- **LOW**: Minor stylistic drift or non-critical trajectory warning.

---

## 4. Run Execution, Pre-Flight, & Regression

1. **Pre-Flight Check (`POST /api/runs/preflight`)**:
   Before launching a run, AgentTrust probes the agent endpoint, validates dataset completeness, ensures the evaluation profile is loaded, and checks provider settings. If any check fails, execution is labeled **BLOCKED** with explicit reasons.
2. **Asynchronous Execution (`EvaluationRunner`)**:
   Runs execute under a controlled concurrency semaphore (`asyncio.Semaphore(concurrency)`) with per-test timeouts and retry limits. If the agent endpoint fails, the test is marked `AGENT_ERROR` (not `CORRECTNESS_FAIL`).
3. **Automated Regression Analysis (`GET /api/runs/{id}/regression`)**:
   When an agent version is evaluated against a dataset with historical runs, the engine cross-references individual test case results against the previous baseline, categorizing tests into:
   - **Regressed**: Previously passing tests that now fail.
   - **Improved**: Previously failing tests that now pass.
   - **Unchanged**: Tests with identical pass/fail status.

---

## 5. Export & Reporting Subsystem

AgentTrust supports three deterministic export formats:
- **CSV Export**: Tabular test-by-test breakdown with individual component scores, latency, and status codes.
- **JSON Export**: Complete machine-readable payload containing run metadata, metrics breakdown, language breakdown, full test results, and methodology disclaimer.
- **13-Section HTML Report**: Self-contained, styled executive report covering:
  1. Executive Summary
  2. Run Information
  3. Overall Metrics
  4. Multilingual Breakdown
  5. Failure Summary & Severity Breakdown
  6. Critical & High Priority Failures
  7. Evidence Grounding Diagnostics
  8. Multilingual Translation Fidelity
  9. Observable Trajectory & Tool Execution
  10. Regression Analysis
  11. Test-Level Execution Catalog
  12. Evaluation Methodology
  13. Scientific & Technical Limitations
