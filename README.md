# AgentTrust

### Multilingual AI Reliability Evaluator
> **Evidence-backed reliability diagnostics for AI agents.**

[![Tests](https://img.shields.io/badge/tests-20%20passed-emerald)](backend/tests)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](backend)
[![Next.js](https://img.shields.io/badge/next.js-14-black)](frontend)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-teal)](backend)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 1. Overview

**AgentTrust** is a standalone, independent evaluation platform for AI agents. Rather than treating evaluation as an opaque LLM prompt that outputs a subjective trust score, AgentTrust treats evaluation as an observable, multi-layered diagnostic pipeline that evaluates an agent's factual correctness, evidence grounding, citation validity, cross-lingual translation fidelity, and observable trajectory integrity.

The core value proposition is:
> **"Turn AI-agent execution into measurable, evidence-backed reliability diagnostics."**

AgentTrust never claims to prove universal trustworthiness. It measures empirical reliability properties under defined benchmark datasets and configurations.

---

## 2. The Core Problem

Production AI agents frequently exhibit deceptive failure modes:
- Generating plausible text while hallucinating statutory dates, numbers, and deadlines.
- Asserting claims that contradict retrieved evidence documents.
- Fabricating citations or referencing sections that do not exist.
- Distorting meaning during multilingual translation (e.g. English $\to$ Hindi / Kannada / Telugu).
- Looping infinitely over tools or omitting required retrieval steps.
- Regressing on existing capabilities when a new model checkpoint or system prompt is deployed.

---

## 3. The AgentTrust Solution

AgentTrust executes an agent against structured benchmark test cases and runs an automated evaluation pipeline:

```text
Benchmark Test Dataset
        ↓
Pre-Flight Readiness Check (Agent reachable? Dataset valid? Profile loaded?)
        ↓
Evaluation Runner (Asynchronous execution with concurrency control)
        ↓
Agent Execution (HTTP REST or in-process Python SDK Adapter)
        ↓
Observable Execution Data (Inputs, Tool Calls, Retrieved Docs, Citations, Outputs)
        ↓
Evaluator Subsystem
 ┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
 ↓              ↓              ↓              ↓              ↓
Correctness    Grounding      Citation       Translation    Trajectory
(Deterministic (Supported /   (Source &      (Back-trans    (Sequence &
+ Semantic)     Contradicted)  Section Check) drift check)   Loop detection)
 └──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
        ↓
Dynamic Metrics & Composite Reliability Score (30/30/15/15/10)
        ↓
Automated Version Regression Analysis & Interactive Failure Drill-down
        ↓
Exportable Diagnostic Reports (13-Section HTML, JSON, CSV)
```

---

## 4. Key Platform Features

- **Authentication & Multi-Tenant Workspaces**: Secure bcrypt password hashing, signed JWT bearer sessions, workspace isolation, and audit logging.
- **Agent Registry & Live Connection Probes**: Register HTTP endpoints or Python SDK agents. Run live health/latency probes (`POST /api/agents/{id}/test-connection`) before starting evaluations.
- **Dataset System with Versioning & Validation**: Semantic versioning (`1.0.0`, `1.1.0`), automated validation checks (missing facts, broken references, translation gaps), and JSON/CSV import.
- **Evidence-Backed Grounding**: Claims are mapped against retrieved documents and classified strictly as `SUPPORTED`, `UNSUPPORTED`, or `CONTRADICTED`. (Unsupported claims are not blindly assumed to be hallucinations).
- **Independent Citation Verification**: Validates whether cited source documents and referenced sections actually exist and corroborate the claim (`VALID`, `INVALID_SOURCE`, `INVALID_SECTION`, `MISMATCH`, `MISSING`).
- **Multilingual Translation Fidelity**: Back-translation and semantic entity preservation across English, Hindi, Kannada, and Telugu.
- **Observable Trajectory Inspection**: Validates tool invocation sequences, loops, and missing retrieval calls without analyzing private chain-of-thought.
- **Pre-Flight Run Verification**: Guarantees agent reachability, dataset integrity, and profile readiness before launching runs (`POST /api/runs/preflight`).
- **Automated Version Regression Testing**: Automatically identifies regressed, improved, and unchanged test cases between agent versions.
- **Explainable Failure Drill-Down**: Side-by-side diagnostic drawer revealing exact claims, citations, retrieved sources, and failure reasons with keyword highlighting.
- **13-Section HTML, CSV, & JSON Reports**: Comprehensive compliance-ready documentation.
- **Zero Fake Metrics**: All metrics are calculated dynamically from actual stored execution data. Demo runs are visibly labeled `DEMO / SIMULATION`.

---

## 5. Agent Integration Interfaces

### Method 1: HTTP Agent REST Protocol
Expose an HTTP endpoint (e.g. `POST https://your-agent.com/run`).

**Request Payload sent by AgentTrust:**
```json
{
  "test_case_id": "KN-001",
  "question": "ನಾಗರಿಕ ಸಭೆ ಪರವಾನಗಿ ಪಡೆಯಲು ಕಾರ್ಯಕ್ರಮಕ್ಕೆ ಎಷ್ಟು ದಿನಗಳ ಮುಂಚಿತವಾಗಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಬೇಕು?",
  "language": "kn",
  "category": "correctness",
  "source_documents": [
    { "document_id": "DOC-CP-001", "section_id": "§4" }
  ]
}
```

**Expected Agent Response Payload:**
```json
{
  "answer": "ನಾಗರಿಕ ಅನುಮತಿಗಳ ನಿರ್ದೇಶನದ §4 ರ ಪ್ರಕಾರ ಕನಿಷ್ಠ 30 ಕ್ಯಾಲೆಂಡರ್ ದಿನಗಳ ಮುಂಚಿತವಾಗಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಬೇಕು.",
  "language": "kn",
  "citations": [
    {
      "document_id": "DOC-CP-001",
      "section": "§4",
      "text": "at least 30 calendar days prior"
    }
  ],
  "retrieved_documents": [
    {
      "document_id": "DOC-CP-001",
      "chunk_id": "chunk_4",
      "text": "Applications must be submitted at least 30 calendar days prior...",
      "score": 0.94
    }
  ],
  "trace": [
    {
      "step": 1,
      "type": "retrieval",
      "tool": "document_search",
      "input": "civic permit application deadline",
      "output": "Found DOC-CP-001 §4"
    },
    {
      "step": 2,
      "type": "tool_call",
      "protocol": "mcp",
      "server": "civic_db",
      "tool": "verify_calendar_days",
      "arguments": { "days": 30 }
    },
    {
      "step": 3,
      "type": "generation"
    }
  ],
  "metadata": {
    "model": "gpt-4o",
    "version": "2.1.0"
  },
  "latency_ms": 285
}
```
*Note: If citations, retrieved documents, or traces are not returned, AgentTrust records "Not provided by agent" instead of fabricating evidence.*

### Method 2: Python SDK Adapter
Implement the `AgentTrustAdapter` interface (`sdk/agenttrust/`):

```python
from sdk.agenttrust import AgentTrustAdapter, AgentRequest, AgentResponse, CitationPayload

class CustomRagAgent(AgentTrustAdapter):
    async def run(self, request: AgentRequest) -> AgentResponse:
        result = await my_agent_pipeline(request.question, language=request.language)
        return AgentResponse(
            answer=result["text"],
            language=request.language,
            citations=[
                CitationPayload(
                    document_id=c["doc_id"],
                    section=c["section"],
                    text=c["snippet"]
                )
                for c in result.get("citations", [])
            ],
            trace=result.get("trace", [])
        )
```
See runnable example in `examples/sample_agent/custom_agent.py`.

---

## 6. Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run backend API server with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The backend initializes the SQLite database automatically (`./agenttrust.db`).
- Interactive OpenAPI Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### 2. Frontend Setup
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 7. Running with Docker Compose

To launch the full production stack (PostgreSQL 16, FastAPI backend, Next.js frontend):

```bash
docker compose up --build
```
- Web Application: [http://localhost:3000](http://localhost:3000)
- REST API Server: [http://localhost:8000](http://localhost:8000)
- PostgreSQL Database: Port 5432

---

## 8. Running Automated Tests

Run the full automated test suite:
```bash
source backend/venv/bin/activate
PYTHONPATH=backend pytest backend/tests -v
```

**Test Coverage (20 tests passed):**
1. Section, date, deadline, number, and authority regex extraction.
2. Citation verification (valid, invalid source, invalid section, mismatch).
3. Evidence grounding classification (`SUPPORTED`, `UNSUPPORTED`, `CONTRADICTED`).
4. Translation fidelity & drift detection across multilingual datasets.
5. Trajectory execution (missing retrieval, redundant loop detection).
6. End-to-end evaluation runner and before/after comparison calculations.
7. Authentication, password hashing, and JWT session handling.
8. Agent connection testing and health probes.
9. Dataset versioning, duplicate cloning, and pre-run validation checks.
10. Run pre-flight verification and automated version regression detection.
11. Python SDK adapter contract compliance.

---

## 9. Evaluation Methodology & Scoring

### Composite Reliability Formula
$$\text{Composite Score} = 0.30 \times C_{\text{corr}} + 0.30 \times G_{\text{ground}} + 0.15 \times C_{\text{cite}} + 0.15 \times T_{\text{trans}} + 0.10 \times T_{\text{traj}}$$

*When translation is not applicable (e.g. English-only test cases), weights are normalized dynamically without penalizing the system.*

### Failure Severity Rubric
- **CRITICAL**: Contradicted verified facts, major numerical/statutory deadline error, or severe translation drift reversing meaning.
- **HIGH**: Substantial unsupported factual claim, incorrect cited section, or significant translation distortion.
- **MEDIUM**: Minor unsupported peripheral claim, formatting citation problem, or trajectory inefficiency.
- **LOW**: Minor stylistic drift or non-critical trajectory warning.

---

## 10. System Boundaries & Scientific Limitations

- **Not Proof of General Trust**: AgentTrust measures selected reliability properties under defined evaluation test cases. It does not certify that an AI model is universally trustworthy.
- **"Unsupported" $\ne$ "Hallucination"**: An unsupported claim means the evaluator found no evidence in the provided evidence set; it does not make universal epistemological claims.
- **No Fabricated Benchmarks**: All scores and deltas displayed in AgentTrust are computed dynamically from actual run execution data.
- **No Private Chain-of-Thought Inspection**: Only observable inputs, tool invocations, retrieved context, and outputs are recorded and audited.

---

## 11. License

Released under the [MIT License](LICENSE).
