from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.seed.seeder import seed_demo_data
from app.models.run import Run
from app.evaluator.runner import EvaluationRunner

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/seed")
async def seed_demo(db: AsyncSession = Depends(get_db)):
    """Seed demo project, documents, agents, and test cases."""
    result = await seed_demo_data(db)
    return result


@router.post("/run")
async def run_one_click_demo(db: AsyncSession = Depends(get_db)):
    """
    One-click complete demo execution:
    1. Ensures demo data is seeded.
    2. Runs evaluation on baseline agent (Run #1: Baseline with simulated errors).
    3. Runs evaluation on optimized agent (Run #2: Optimized with 0 errors).
    Returns run IDs ready for dashboard rendering and before/after comparison.
    """
    seed_res = await seed_demo_data(db)
    project_id = seed_res["project_id"]
    baseline_agent_id = seed_res["baseline_agent_id"]
    optimized_agent_id = seed_res["optimized_agent_id"]
    dataset_id = seed_res["dataset_id"]

    runner = EvaluationRunner(db)

    # Run 1: Baseline
    run_1 = Run(
        project_id=project_id,
        agent_id=baseline_agent_id,
        dataset_id=dataset_id,
        agent_version="1.0.0-baseline",
        dataset_version="1.0.0",
        evaluators_config={"correctness": True, "grounding": True, "citation": True, "translation": True, "trajectory": True},
        status="PENDING"
    )
    db.add(run_1)
    await db.commit()
    await db.refresh(run_1)

    completed_run_1 = await runner.execute_run(run_1.id)

    # Run 2: Optimized (for immediate comparison capability)
    run_2 = Run(
        project_id=project_id,
        agent_id=optimized_agent_id,
        dataset_id=dataset_id,
        agent_version="2.0.0-optimized",
        dataset_version="1.0.0",
        evaluators_config={"correctness": True, "grounding": True, "citation": True, "translation": True, "trajectory": True},
        status="PENDING"
    )
    db.add(run_2)
    await db.commit()
    await db.refresh(run_2)

    completed_run_2 = await runner.execute_run(run_2.id)

    return {
        "status": "SUCCESS",
        "message": "Demo evaluation executed successfully across baseline and optimized agents.",
        "project_id": project_id,
        "baseline_run_id": completed_run_1.id,
        "baseline_score": completed_run_1.composite_score,
        "optimized_run_id": completed_run_2.id,
        "optimized_score": completed_run_2.composite_score
    }
