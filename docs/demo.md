# AgentTrust Demo Walkthrough

AgentTrust includes a completely self-contained demo environment that operates without requiring external API keys.

---

## 1. One-Click Demo Execution

You can trigger the entire demo in one step either from the UI or via API:

### Via Frontend UI
1. Click the **"Run Demo"** button in the top navigation bar or **"Start Demo Evaluation"** on the home page.
2. The platform automatically:
   - Initializes the database schema.
   - Loads the 4 statutory policy documents (`data/demo_documents/`).
   - Loads the 32 multilingual test cases (`data/demo_test_cases.json`).
   - Registers both the **Baseline Agent** (v1.0.0 with controlled failure simulation modes) and the **Optimized Agent** (v2.0.0 with corrected prompt constraints).
   - Executes the evaluation pipeline across all 32 tests and 4 languages.
   - Redirects to the completed run dashboard.

### Via API
```bash
curl -X POST http://localhost:8000/api/demo/run
```

Response:
```json
{
  "status": "SUCCESS",
  "project_id": "...",
  "baseline_run_id": "...",
  "baseline_score": 0.812,
  "optimized_run_id": "...",
  "optimized_score": 0.985
}
```

---

## 2. Navigating the Demo Diagnostics

### Step 1: Overall Dashboard (`/runs/{run_id}`)
- Inspect the **Composite Reliability Score** (weighted formula: Correctness 30%, Grounding 30%, Citation 15%, Translation 15%, Trajectory 10%).
- View the 5 Evaluator cards.

### Step 2: Failure Drill-Down
- Click on any failed test in the **Test Case Results** table.
- A full investigation drawer opens showing:
  - **Question**: e.g., *"What is the standard permit filing timeline for public gatherings exceeding 150 attendees?"*
  - **Agent Answer**: *"Applications must be submitted within 60 calendar days under §18."*
  - **Expected Fact**: *"30 calendar days"*
  - **Retrieved Source**: *"Applications ... must be submitted at least 30 calendar days prior ... (§4)"*
  - **Result**: `CONTRADICTED`
  - **Severity**: `CRITICAL`
  - **Exact Diagnostic Reason**: Explains why the claim contradicted the retrieved source.

### Step 3: Multilingual Analysis
- View performance across **English**, **Kannada**, **Hindi**, and **Telugu**.
- Observe how translation drift is diagnosed via back-translation.

### Step 4: Before / After Comparison (`/compare`)
- View the differential comparison between **Baseline Run** (v1.0.0) and **Optimized Run** (v2.0.0).
- Net improvements and regressions are clearly highlighted with dynamic deltas (e.g. `+17.3%`).
