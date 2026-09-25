import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from app.main import app
from app.database import init_db, AsyncSessionLocal
from app.models.run import Run
from app.evaluator.runner import EvaluationRunner


@pytest.mark.asyncio
async def test_full_evaluation_run_and_comparison():
    await init_db()

    async with AsyncSessionLocal() as session:
        # Seed demo data
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            seed_res = await ac.post("/api/demo/seed")
            assert seed_res.status_code == 200
            seed_data = seed_res.json()

        project_id = seed_data["project_id"]
        baseline_agent_id = seed_data["baseline_agent_id"]
        optimized_agent_id = seed_data["optimized_agent_id"]
        dataset_id = seed_data["dataset_id"]

        runner = EvaluationRunner(session)

        # Execute Run 1 (Baseline)
        run_1 = Run(
            project_id=project_id,
            agent_id=baseline_agent_id,
            dataset_id=dataset_id,
            agent_version="1.0.0-baseline",
            dataset_version="1.0.0",
            status="PENDING"
        )
        session.add(run_1)
        await session.commit()
        await session.refresh(run_1)

        completed_1 = await runner.execute_run(run_1.id)
        assert completed_1.status == "COMPLETED"
        assert completed_1.completed_tests == 32
        assert completed_1.composite_score is not None

        # Execute Run 2 (Optimized)
        run_2 = Run(
            project_id=project_id,
            agent_id=optimized_agent_id,
            dataset_id=dataset_id,
            agent_version="2.0.0-optimized",
            dataset_version="1.0.0",
            status="PENDING"
        )
        session.add(run_2)
        await session.commit()
        await session.refresh(run_2)

        completed_2 = await runner.execute_run(run_2.id)
        assert completed_2.status == "COMPLETED"
        assert completed_2.completed_tests == 32
        # Optimized agent should achieve higher composite score
        assert completed_2.composite_score >= completed_1.composite_score

        # Test Compare Endpoint
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            compare_res = await ac.get(f"/api/runs/{completed_1.id}/compare/{completed_2.id}")
            assert compare_res.status_code == 200
            comp = compare_res.json()
            assert "metrics" in comp
            assert "composite_score" in comp["metrics"]
            assert comp["metrics"]["composite_score"]["delta"] >= 0

            # Test Report Endpoints
            html_res = await ac.get(f"/api/reports/{completed_1.id}/html")
            assert html_res.status_code == 200
            assert "AgentTrust Reliability Evaluation Report" in html_res.text

            json_res = await ac.get(f"/api/reports/{completed_1.id}/json")
            assert json_res.status_code == 200
            assert "evaluation_platform" in json_res.json()

            csv_res = await ac.get(f"/api/reports/{completed_1.id}/csv")
            assert csv_res.status_code == 200
            assert "Test ID,Language,Overall Status" in csv_res.text
