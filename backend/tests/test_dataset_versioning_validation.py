import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_dataset_versioning_and_validation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create Project
        p_res = await ac.post("/api/projects", json={"name": "Dataset Validation Project"})
        assert p_res.status_code == 200
        project_id = p_res.json()["id"]

        # Create Dataset
        d_res = await ac.post("/api/datasets", json={"project_id": project_id, "name": "Benchmark V1", "version": "1.0.0"})
        assert d_res.status_code == 201
        dataset_id = d_res.json()["id"]

        # Add valid test case
        tc1_payload = {
            "external_id": "VAL-001",
            "language": "en",
            "question": "What is the statutory deadline for filing complaints?",
            "expected_answer": "Complaints must be submitted within 30 calendar days.",
            "source_documents": [{"document_id": "CIVIC-ACT-2024", "section_id": "Section 12(a)"}],
            "required_facts": [{"id": "fact-1", "type": "number", "expected": "30"}],
            "potential_traps": ["60 days"]
        }
        tc1_res = await ac.post(f"/api/datasets/{dataset_id}/test-cases", json=tc1_payload)
        assert tc1_res.status_code == 201

        # Validate dataset - should be valid
        val_res = await ac.get(f"/api/datasets/{dataset_id}/validate")
        assert val_res.status_code == 200
        val_data = val_res.json()
        assert val_data["is_valid"] is True
        assert val_data["total_test_cases"] == 1
        assert val_data["errors_count"] == 0

        # Publish version 1.1.0
        ver_res = await ac.post(f"/api/datasets/{dataset_id}/versions", json={"version": "1.1.0", "changelog": "Added statutory complaint deadline"})
        assert ver_res.status_code == 201
        assert ver_res.json()["version"] == "1.1.0"

        # Duplicate dataset
        dup_res = await ac.post(f"/api/datasets/{dataset_id}/duplicate")
        assert dup_res.status_code == 201
        dup_data = dup_res.json()
        assert dup_data["name"] == "Benchmark V1 (Copy)"
        assert dup_data["test_cases_count"] == 1
