import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db
from app.services import retrieval

# Reset singleton document store to ensure correct DATA_DIR is loaded
retrieval._document_store = None


@pytest.mark.asyncio
async def test_root_and_health():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/")
        assert res.status_code == 200
        assert res.json()["product"] == "AgentTrust"

        health = await ac.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_projects_crud():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_res = await ac.post("/api/projects", json={"name": "Test Project", "description": "Unit testing"})
        assert create_res.status_code == 200
        proj = create_res.json()
        assert proj["name"] == "Test Project"
        proj_id = proj["id"]

        list_res = await ac.get("/api/projects")
        assert list_res.status_code == 200
        assert any(p["id"] == proj_id for p in list_res.json())


@pytest.mark.asyncio
async def test_demo_seed_and_one_click():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Seed test
        seed_res = await ac.post("/api/demo/seed")
        assert seed_res.status_code == 200
        data = seed_res.json()
        assert "project_id" in data
        assert "baseline_agent_id" in data
        assert "dataset_id" in data

        # Check seeded dataset test cases
        ds_id = data["dataset_id"]
        tc_res = await ac.get(f"/api/datasets/{ds_id}/test-cases")
        assert tc_res.status_code == 200
        test_cases = tc_res.json()
        assert len(test_cases) == 32
