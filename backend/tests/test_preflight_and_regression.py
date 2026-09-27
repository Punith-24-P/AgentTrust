import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_preflight_check_and_regression_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        p_res = await ac.post("/api/projects", json={"name": "Preflight & Regression Project"})
        project_id = p_res.json()["id"]

        ag_res = await ac.post("/api/agents", json={
            "project_id": project_id,
            "name": "Regression Test Agent",
            "adapter_type": "demo",
            "version": "1.0.0"
        })
        agent_id = ag_res.json()["id"]

        ds_res = await ac.post("/api/datasets", json={"project_id": project_id, "name": "Regression Dataset"})
        dataset_id = ds_res.json()["id"]

        # Preflight on empty dataset should be BLOCKED
        pf_empty = await ac.post("/api/runs/preflight", json={"agent_id": agent_id, "dataset_id": dataset_id})
        assert pf_empty.status_code == 200
        assert pf_empty.json()["status"] == "BLOCKED"

        # Add test cases
        await ac.post(f"/api/datasets/{dataset_id}/test-cases", json={
            "external_id": "REG-01",
            "language": "en",
            "question": "What is the filing window?",
            "expected_answer": "30 days",
            "required_facts": [{"id": "f1", "type": "number", "expected": "30"}]
        })

        # Preflight on populated dataset should be READY
        pf_ready = await ac.post("/api/runs/preflight", json={"agent_id": agent_id, "dataset_id": dataset_id})
        assert pf_ready.status_code == 200
        assert pf_ready.json()["status"] == "READY"
