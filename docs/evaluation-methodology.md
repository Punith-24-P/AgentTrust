# AgentTrust Evaluation Methodology

This document outlines the evaluation methodology, diagnostic categories, scoring formulas, and severity classifications implemented in AgentTrust.

---

## 1. Core Principles

1. **Evidence-Backed Diagnostics**: Every failure must be attributable to a specific claim, source section, missing required fact, or execution anomaly.
2. **What AgentTrust Measures**:
   - Whether the agent's observable response satisfies defined statutory conditions.
   - Whether claims are supported by available retrieved evidence.
   - Whether cited sources exist and substantiate claims.
   - Whether statutory meaning is preserved across translations.
   - Whether tool usage followed an optimal, non-repetitive sequence.
3. **What AgentTrust Does NOT Claim**:
   - AgentTrust does **not** claim to prove an AI is universally trustworthy.
   - "Unsupported" does not prove hallucination; it means the claim could not be verified in the provided evidence set.
   - Overall scores are composite evaluation scores under defined weights, not absolute measures of truth.

---

## 2. Evaluation Pillars

### 2.1 Correctness Evaluator
- **Layer A (Deterministic Checks)**: Uses robust regex parsing to extract numbers, statutory section marks (§), authorities, and deadlines. Compares them strictly against expected facts.
- **Layer B (Semantic Evaluation)**: Evaluates semantic equivalence using an LLM judge or deterministic heuristic fallback.
- **Status Output**: `PASS`, `PARTIAL`, `FAIL`.

### 2.2 Grounding Evaluator
- Compares claims in the agent output against the retrieved evidence text.
- **Allowed Classifications**:
  - `SUPPORTED`: Evidence directly substantiates the claim.
  - `UNSUPPORTED`: Claim is not present in the retrieved evidence.
  - `CONTRADICTED`: Claim directly conflicts with retrieved evidence (e.g. 60 days vs 30 days).

### 2.3 Citation Verification
- Inspects cited documents (e.g. `DOC-CP-001 §4`).
- **Verifications**:
  1. Does the cited document exist in the statutory repository?
  2. Does the cited section exist within the document?
  3. Does the citation match the expected governing source?
  4. Does the cited evidence support the associated claim?
- **Status Output**: `VALID`, `INVALID_SOURCE`, `INVALID_SECTION`, `MISMATCH`, `UNSUPPORTED`, `MISSING`.

### 2.4 Translation Fidelity Evaluator
- Evaluates non-English responses (Kannada `kn`, Hindi `hi`, Telugu `te`).
- Performs back-translation to English.
- Compares statutory entities, numbers, dates, permissions, and prohibitions.
- **Status Output**:
  - `PASS`: Full semantic preservation.
  - `MINOR_DRIFT`: Secondary entity phrasing variance.
  - `MAJOR_DRIFT`: Core numbers, deadlines, or prohibitions distorted.

### 2.5 Trajectory Evaluator
- Evaluates observable trace events (`agent_start`, `retrieval`, `tool_call`, `generation`, `agent_end`).
- Verifies retrieval was performed when required.
- Detects redundant loops (identical tool call repeated without progress).
- Verifies chronological sequence (retrieval precedes generation).
- **Status Output**: `PASS`, `WARNING`, `FAIL`.

---

## 3. Composite Reliability Score Formula

The default weighted formula:

$$\text{Composite Score} = 0.30 \times \text{Correctness} + 0.30 \times \text{Grounding} + 0.15 \times \text{Citation} + 0.15 \times \text{Translation} + 0.10 \times \text{Trajectory}$$

*Note: For English tests (where translation is not applicable), weights are normalized: Correctness 35%, Grounding 35%, Citation 15%, Trajectory 15%.*

---

## 4. Failure Severity Classification

| Severity | Criteria |
| :--- | :--- |
| **CRITICAL** | Contradicted important factual claim in Grounding |
| **HIGH** | Wrong required statutory fact in Correctness OR Major Translation Drift |
| **MEDIUM** | Citation mismatch / Invalid source OR Important unsupported claim |
| **LOW** | Trajectory loop warning OR Minor translation drift |
