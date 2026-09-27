import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_agent_registration_and_connection_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        p_res = await ac.post("/api/projects", json={"name": "Agent Connectivity Project"})
        project_id = p_res.json()["id"]

        # Register demo agent
        demo_ag_res = await ac.post("/api/agents", json={
            "project_id": project_id,
            "name": "Local Demo Agent",
            "adapter_type": "demo",
            "version": "1.0.0",
            "model": "rule-based-evaluator"
        })
        assert demo_ag_res.status_code == 201
        demo_agent_id = demo_ag_res.json()["id"]

        # Test connection for demo agent
        test_conn_res = await ac.post(f"/api/agents/{demo_agent_id}/test-connection")
        assert test_conn_res.status_code == 200
        conn_data = test_conn_res.json()
        assert conn_data["status"] == "SUCCESS"
        assert conn_data["latency_ms"] >= 0

        # Register HTTP agent with unreachable endpoint
        http_ag_res = await ac.post("/api/agents", json={
            "project_id": project_id,
            "name": "Remote HTTP Agent",
            "adapter_type": "http",
            "endpoint": "http://127.0.0.1:59999/nonexistent-agent",
            "version": "2.0.0"
        })
        assert http_ag_res.status_code == 201
        http_agent_id = http_ag_res.json()["id"]

        # Test connection for unreachable agent - should return ERROR status without crashing
        test_http_conn = await ac.post(f"/api/agents/{http_agent_id}/test-connection")
        assert test_http_conn.status_code == 200
        http_conn_data = test_http_conn.json()
        assert http_conn_data["status"] == "ERROR"
        assert "error" in http_conn_data["details"]
