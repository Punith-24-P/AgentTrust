from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db, AsyncSessionLocal
from app.models.run import Run, AgentRun, RunMetric
from app.models.agent import Agent
from app.models.dataset import Dataset, TestCase
from app.models.evaluation import EvaluationResult, ClaimResult, CitationResult
from app.models.trace import TraceEvent
from app.schemas.run import RunCreate, RunResponse, AgentRunDetailResponse, RunComparisonResponse
from app.evaluator.runner import EvaluationRunner
from app.evaluator.metrics import MetricsEngine

router = APIRouter(tags=["runs"])


async def run_evaluation_task(run_id: str):
    async with AsyncSessionLocal() as session:
        try:
            runner = EvaluationRunner(session)
            await runner.execute_run(run_id)
        except Exception as e:
            print(f"Error executing run {run_id}: {e}")
            q = select(Run).where(Run.id == run_id)
            res = await session.execute(q)
            run = res.scalars().first()
            if run:
                run.status = "FAILED"
                run.error_message = str(e)
                await session.commit()


@router.post("/runs", response_model=RunResponse)
async def create_run(data: RunCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    # Verify agent and dataset exist
    ag_res = await db.execute(select(Agent).where(Agent.id == data.agent_id))
    agent = ag_res.scalars().first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    ds_res = await db.execute(select(Dataset).where(Dataset.id == data.dataset_id))
    dataset = ds_res.scalars().first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    run = Run(
        project_id=data.project_id,
        agent_id=data.agent_id,
        dataset_id=data.dataset_id,
        agent_version=agent.version,
        dataset_version=dataset.version,
        evaluators_config=data.evaluators_config.model_dump() if data.evaluators_config else {},
        status="PENDING"
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    # Launch evaluation runner in background
    background_tasks.add_task(run_evaluation_task, run.id)

    run_dict = {
        **run.__dict__,
        "agent_name": agent.name,
        "dataset_name": dataset.name
    }
    return RunResponse(**run_dict)


@router.get("/runs", response_model=List[RunResponse])
async def list_runs(project_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    q = select(Run)
    if project_id:
        q = q.where(Run.project_id == project_id)
    q = q.order_by(Run.created_at.desc())
    res = await db.execute(q)
    runs = res.scalars().all()

    output = []
    for r in runs:
        ag = (await db.execute(select(Agent.name).where(Agent.id == r.agent_id))).scalar()
        ds = (await db.execute(select(Dataset.name).where(Dataset.id == r.dataset_id))).scalar()
        r_dict = {
            "id": r.id,
            "project_id": r.project_id,
            "agent_id": r.agent_id,
            "dataset_id": r.dataset_id,
            "agent_version": r.agent_version,
            "dataset_version": r.dataset_version,
            "status": r.status,
            "evaluators_config": r.evaluators_config or {},
            "total_tests": r.total_tests,
            "completed_tests": r.completed_tests,
            "composite_score": r.composite_score,
            "duration_seconds": r.duration_seconds,
            "started_at": r.started_at,
            "completed_at": r.completed_at,
            "error_message": r.error_message,
            "created_at": r.created_at,
            "agent_name": ag or "Unknown Agent",
            "dataset_name": ds or "Unknown Dataset"
        }
        output.append(RunResponse(**r_dict))
    return output


@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_run(run_id: str, db: AsyncSession = Depends(get_db)):
    q = select(Run).where(Run.id == run_id)
    res = await db.execute(q)
    r = res.scalars().first()
    if not r:
        raise HTTPException(status_code=404, detail="Run not found")

    ag = (await db.execute(select(Agent.name).where(Agent.id == r.agent_id))).scalar()
    ds = (await db.execute(select(Dataset.name).where(Dataset.id == r.dataset_id))).scalar()
    return RunResponse(
        id=r.id,
        project_id=r.project_id,
        agent_id=r.agent_id,
        dataset_id=r.dataset_id,
        agent_version=r.agent_version,
        dataset_version=r.dataset_version,
        status=r.status,
        evaluators_config=r.evaluators_config or {},
        total_tests=r.total_tests,
        completed_tests=r.completed_tests,
        composite_score=r.composite_score,
        duration_seconds=r.duration_seconds,
        started_at=r.started_at,
        completed_at=r.completed_at,
        error_message=r.error_message,
        created_at=r.created_at,
        agent_name=ag or "Unknown Agent",
        dataset_name=ds or "Unknown Dataset"
    )


@router.get("/runs/{run_id}/results")
async def get_run_results(
    run_id: str,
    language: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    evaluator: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Returns full test case results for a run, with filter support.
    """
    q = (
        select(AgentRun)
        .where(AgentRun.run_id == run_id)
        .options(
            selectinload(AgentRun.test_case),
            selectinload(AgentRun.evaluation_result).selectinload(EvaluationResult.claims),
            selectinload(AgentRun.evaluation_result).selectinload(EvaluationResult.citations),
            selectinload(AgentRun.trace_events)
        )
    )
    res = await db.execute(q)
    agent_runs = res.scalars().all()

    filtered = []
    for ar in agent_runs:
        ev = ar.evaluation_result
        tc = ar.test_case

        if not ev or not tc:
            continue

        if language and ar.language.lower() != language.lower():
            continue

        if status and ev.overall_status.upper() != status.upper():
            continue

        if severity and ev.severity.upper() != severity.upper():
            continue

        if evaluator:
            ev_status = getattr(ev, f"{evaluator.lower()}_status", None)
            if ev_status and ev_status.upper() == "PASS":
                continue  # Filter for failures in this evaluator

        if search:
            search_lower = search.lower()
            if search_lower not in tc.question.lower() and search_lower not in ar.final_answer.lower() and search_lower not in tc.external_id.lower():
                continue

        filtered.append({
            "id": ar.id,
            "run_id": ar.run_id,
            "test_case_id": ar.test_case_id,
            "external_id": tc.external_id,
            "category": tc.category,
            "language": ar.language,
            "question": tc.question,
            "expected_answer": tc.expected_answer,
            "final_answer": ar.final_answer,
            "latency_ms": ar.latency_ms,
            "status": ar.status,
            "retrieved_documents": ar.retrieved_documents or [],
            "citations": ar.citations or [],
            "evaluation_result": {
                "id": ev.id,
                "overall_status": ev.overall_status,
                "composite_score": ev.composite_score,
                "severity": ev.severity,
                "correctness_status": ev.correctness_status,
                "correctness_score": ev.correctness_score,
                "correctness_reason": ev.correctness_reason,
                "deterministic_score": ev.deterministic_score,
                "semantic_score": ev.semantic_score,
                "grounding_status": ev.grounding_status,
                "grounding_score": ev.grounding_score,
                "grounding_reason": ev.grounding_reason,
                "citation_status": ev.citation_status,
                "citation_score": ev.citation_score,
                "citation_reason": ev.citation_reason,
                "translation_status": ev.translation_status,
                "translation_score": ev.translation_score,
                "translation_reason": ev.translation_reason,
                "back_translation": ev.back_translation,
                "trajectory_status": ev.trajectory_status,
                "trajectory_score": ev.trajectory_score,
                "trajectory_reason": ev.trajectory_reason,
                "claims": [
                    {
                        "claim_text": c.claim_text,
                        "status": c.status,
                        "document_id": c.document_id,
                        "section_id": c.section_id,
                        "evidence_text": c.evidence_text,
                        "reason": c.reason
                    }
                    for c in ev.claims
                ],
                "citations": [
                    {
                        "citation_text": cit.citation_text,
                        "status": cit.status,
                        "document_id": cit.document_id,
                        "section_id": cit.section_id,
                        "evidence_matches": cit.evidence_matches,
                        "reason": cit.reason
                    }
                    for cit in ev.citations
                ]
            },
            "trace_events": [
                {
                    "step": te.step,
                    "event_type": te.event_type,
                    "input_data": te.input_data,
                    "output_data": te.output_data,
                    "metadata_json": te.metadata_json,
                    "timestamp": te.timestamp.isoformat()
                }
                for te in sorted(ar.trace_events, key=lambda x: x.step)
            ]
        })

    return filtered


@router.get("/results/{result_id}")
async def get_single_result_drilldown(result_id: str, db: AsyncSession = Depends(get_db)):
    """
    Returns complete failure drill-down view for a specific AgentRun.
    """
    q = (
        select(AgentRun)
        .where(AgentRun.id == result_id)
        .options(
            selectinload(AgentRun.test_case),
            selectinload(AgentRun.evaluation_result).selectinload(EvaluationResult.claims),
            selectinload(AgentRun.evaluation_result).selectinload(EvaluationResult.citations),
            selectinload(AgentRun.trace_events)
        )
    )
    res = await db.execute(q)
    ar = res.scalars().first()
    if not ar:
        raise HTTPException(status_code=404, detail="Test result not found")

    tc = ar.test_case
    ev = ar.evaluation_result

    return {
        "id": ar.id,
        "run_id": ar.run_id,
        "test_case_id": tc.external_id if tc else ar.test_case_id,
        "language": ar.language,
        "question": tc.question if tc else "",
        "expected_answer": tc.expected_answer if tc else "",
        "required_facts": tc.required_facts if tc else [],
        "potential_traps": tc.potential_traps if tc else [],
        "agent_answer": ar.final_answer,
        "retrieved_documents": ar.retrieved_documents or [],
        "citations": ar.citations or [],
        "evaluation": {
            "overall_status": ev.overall_status if ev else "UNKNOWN",
            "composite_score": ev.composite_score if ev else 0.0,
            "severity": ev.severity if ev else "LOW",
            "correctness": {
                "status": ev.correctness_status if ev else "UNKNOWN",
                "score": ev.correctness_score if ev else 0.0,
                "reason": ev.correctness_reason if ev else "",
                "deterministic_score": ev.deterministic_score if ev else 0.0,
                "semantic_score": ev.semantic_score if ev else 0.0
            },
            "grounding": {
                "status": ev.grounding_status if ev else "UNKNOWN",
                "score": ev.grounding_score if ev else 0.0,
                "reason": ev.grounding_reason if ev else "",
                "claims": [
                    {
                        "claim": c.claim_text,
                        "status": c.status,
                        "document_id": c.document_id,
                        "section_id": c.section_id,
                        "evidence": c.evidence_text,
                        "reason": c.reason
                    }
                    for c in (ev.claims if ev else [])
                ]
            },
            "citation": {
                "status": ev.citation_status if ev else "UNKNOWN",
                "score": ev.citation_score if ev else 0.0,
                "reason": ev.citation_reason if ev else "",
                "citations": [
                    {
                        "citation": c.citation_text,
                        "status": c.status,
                        "document_id": c.document_id,
                        "section_id": c.section_id,
                        "evidence_matches": c.evidence_matches,
                        "reason": c.reason
                    }
                    for c in (ev.citations if ev else [])
                ]
            },
            "translation": {
                "status": ev.translation_status if ev else "UNKNOWN",
                "score": ev.translation_score if ev else 0.0,
                "reason": ev.translation_reason if ev else "",
                "back_translation": ev.back_translation if ev else ""
            },
            "trajectory": {
                "status": ev.trajectory_status if ev else "UNKNOWN",
                "score": ev.trajectory_score if ev else 0.0,
                "reason": ev.trajectory_reason if ev else "",
                "retrieval_executed": ev.retrieval_executed if ev else False,
                "loop_detected": ev.loop_detected if ev else False,
                "sequence_valid": ev.sequence_valid if ev else True
            }
        },
        "trace": [
            {
                "step": te.step,
                "event_type": te.event_type,
                "input_data": te.input_data,
                "output_data": te.output_data,
                "timestamp": te.timestamp.isoformat()
            }
            for te in sorted(ar.trace_events, key=lambda x: x.step)
        ]
    }


@router.get("/runs/{run_id}/metrics")
async def get_run_metrics(run_id: str, db: AsyncSession = Depends(get_db)):
    q = select(RunMetric).where(RunMetric.run_id == run_id)
    res = await db.execute(q)
    metric = res.scalars().first()
    if not metric:
        raise HTTPException(status_code=404, detail="Metrics not yet computed or run in progress")
    return metric.metrics_json


@router.get("/runs/{before_run_id}/compare/{after_run_id}", response_model=RunComparisonResponse)
async def compare_runs(before_run_id: str, after_run_id: str, db: AsyncSession = Depends(get_db)):
    """
    Dynamically compares two runs (baseline vs after), computing honest deltas across all metrics.
    """
    b_m = (await db.execute(select(RunMetric).where(RunMetric.run_id == before_run_id))).scalars().first()
    a_m = (await db.execute(select(RunMetric).where(RunMetric.run_id == after_run_id))).scalars().first()

    if not b_m or not a_m:
        raise HTTPException(status_code=404, detail="One or both runs lack computed metrics.")

    b_run = (await db.execute(select(Run).where(Run.id == before_run_id))).scalars().first()
    a_run = (await db.execute(select(Run).where(Run.id == after_run_id))).scalars().first()

    b_ag = (await db.execute(select(Agent).where(Agent.id == b_run.agent_id))).scalars().first()
    a_ag = (await db.execute(select(Agent).where(Agent.id == a_run.agent_id))).scalars().first()

    comparison = MetricsEngine.compare_runs(b_m.metrics_json, a_m.metrics_json)

    return RunComparisonResponse(
        before_run_id=before_run_id,
        after_run_id=after_run_id,
        before_agent_name=b_ag.name if b_ag else "Baseline Agent",
        after_agent_name=a_ag.name if a_ag else "After Agent",
        before_version=b_run.agent_version,
        after_version=a_run.agent_version,
        metrics=comparison["metrics"],
        language_deltas=comparison["language_deltas"]
    )
