# AgentTrust REST API Reference

Base URL: `http://localhost:8000/api`

---

## 1. Projects
- `POST /api/projects`: Create project workspace.
  ```json
  { "name": "Aethelgard Civic", "description": "Legal QA tests" }
  ```
- `GET /api/projects`: List projects.
- `GET /api/projects/{id}`: Get project details.

---

## 2. Agents
- `POST /api/agents`: Register an agent (Demo or External HTTP).
  ```json
  {
    "project_id": "...",
    "name": "LegalAssistant-Prod",
    "adapter_type": "http",
    "endpoint": "https://agent.example.com/api/run",
    "version": "1.2.0",
    "model": "gpt-4o-mini",
    "supported_languages": ["en", "kn", "hi", "te"]
  }
  ```
- `GET /api/agents`: List registered agents.
- `GET /api/agents/{id}`: Get agent metadata.

---

## 3. Datasets & Test Cases
- `POST /api/datasets`: Create a test suite dataset.
- `GET /api/datasets`: List datasets with test case counts.
- `GET /api/datasets/{id}/test-cases`: List test cases (supports `?language=kn`).
- `POST /api/datasets/{id}/test-cases`: Create individual structured test case.
- `POST /api/datasets/{id}/import-json`: Bulk import test cases from JSON.

---

## 4. Evaluation Runs
- `POST /api/runs`: Launch evaluation run asynchronously.
  ```json
  {
    "project_id": "...",
    "agent_id": "...",
    "dataset_id": "...",
    "evaluators_config": {
      "correctness": true,
      "grounding": true,
      "citation": true,
      "translation": true,
      "trajectory": true
    }
  }
  ```
- `GET /api/runs`: List runs.
- `GET /api/runs/{id}`: Run overview and status.
- `GET /api/runs/{id}/results`: Filterable test case evaluation results (`?language=hi&status=FAIL&severity=CRITICAL`).
- `GET /api/results/{result_id}`: Full failure drill-down view with evidence snippets.
- `GET /api/runs/{run_id}/metrics`: Dynamic metrics summary.
- `GET /api/runs/{before_id}/compare/{after_id}`: Dynamic before/after comparison with delta percentages.

---

## 5. Reports & Exports
- `GET /api/reports/{run_id}/html`: Self-contained styled HTML report.
- `GET /api/reports/{run_id}/json`: Machine-readable JSON export.
- `GET /api/reports/{run_id}/csv`: Test-level CSV summary.

---

## 6. One-Click Demo
- `POST /api/demo/seed`: Seed demo project, documents, test cases, and agents.
- `POST /api/demo/run`: One-click execution of both baseline and optimized runs.
