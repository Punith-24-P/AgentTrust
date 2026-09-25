from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.run import Run, AgentRun, RunMetric
from app.models.agent import Agent
from app.models.dataset import Dataset
from app.models.evaluation import EvaluationResult
from app.services.report import ReportGenerator

router = APIRouter(prefix="/reports", tags=["reports"])


async def _fetch_run_full_data(run_id: str, db: AsyncSession):
    q_run = select(Run).where(Run.id == run_id)
    r = (await db.execute(q_run)).scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="Run not found")

    ag = (await db.execute(select(Agent.name).where(Agent.id == r.agent_id))).scalar()
    ds = (await db.execute(select(Dataset.name).where(Dataset.id == r.dataset_id))).scalar()

    run_dict = {
        "id": r.id,
        "agent_name": ag or "Demo Agent",
        "agent_version": r.agent_version,
        "dataset_name": ds or "Demo Dataset",
        "dataset_version": r.dataset_version,
        "status": r.status,
        "composite_score": r.composite_score,
        "completed_at": r.completed_at.isoformat() if r.completed_at else None
    }

    # Fetch metric
    m = (await db.execute(select(RunMetric).where(RunMetric.run_id == run_id))).scalars().first()
    metrics_json = m.metrics_json if m else {}

    # Fetch results
    q_results = (
        select(AgentRun)
        .where(AgentRun.run_id == run_id)
        .options(
            selectinload(AgentRun.test_case),
            selectinload(AgentRun.evaluation_result).selectinload(EvaluationResult.claims),
            selectinload(AgentRun.evaluation_result).selectinload(EvaluationResult.citations)
        )
    )
    ar_list = (await db.execute(q_results)).scalars().all()

    results_data = []
    for ar in ar_list:
        tc = ar.test_case
        ev = ar.evaluation_result
        if not ev or not tc:
            continue
        results_data.append({
            "test_case_id": tc.external_id,
            "language": ar.language,
            "final_answer": ar.final_answer,
            "latency_ms": ar.latency_ms,
            "test_case": {
                "external_id": tc.external_id,
                "language": tc.language,
                "question": tc.question,
                "expected_answer": tc.expected_answer
            },
            "evaluation_result": {
                "overall_status": ev.overall_status,
                "composite_score": ev.composite_score,
                "severity": ev.severity,
                "correctness_status": ev.correctness_status,
                "correctness_score": ev.correctness_score,
                "correctness_reason": ev.correctness_reason,
                "grounding_status": ev.grounding_status,
                "grounding_score": ev.grounding_score,
                "grounding_reason": ev.grounding_reason,
                "citation_status": ev.citation_status,
                "citation_score": ev.citation_score,
                "citation_reason": ev.citation_reason,
                "translation_status": ev.translation_status,
                "translation_score": ev.translation_score,
                "translation_reason": ev.translation_reason,
                "trajectory_status": ev.trajectory_status,
                "trajectory_score": ev.trajectory_score
            }
        })

    return run_dict, metrics_json, results_data


@router.get("/{run_id}/html", response_class=HTMLResponse)
async def get_html_report(run_id: str, db: AsyncSession = Depends(get_db)):
    run_dict, metrics_json, results_data = await _fetch_run_full_data(run_id, db)
    html_content = ReportGenerator.generate_html_report(run_dict, results_data, metrics_json)
    return HTMLResponse(content=html_content)


@router.get("/{run_id}/json")
async def get_json_export(run_id: str, db: AsyncSession = Depends(get_db)):
    run_dict, metrics_json, results_data = await _fetch_run_full_data(run_id, db)
    json_str = ReportGenerator.generate_json_export(run_dict, results_data, metrics_json)
    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=agenttrust_report_{run_id[:8]}.json"}
    )


@router.get("/{run_id}/csv")
async def get_csv_export(run_id: str, db: AsyncSession = Depends(get_db)):
    run_dict, metrics_json, results_data = await _fetch_run_full_data(run_id, db)
    csv_str = ReportGenerator.generate_csv_export(results_data)
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=agenttrust_results_{run_id[:8]}.csv"}
    )
