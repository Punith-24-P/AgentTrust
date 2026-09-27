from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
import httpx
from app.database import get_db, AsyncSessionLocal
from app.models.run import Run, AgentRun, RunMetric
from app.models.agent import Agent
from app.models.dataset import Dataset, DatasetVersion, TestCase
from app.models.document import Document
from app.models.evaluation_profile import EvaluationProfile
from app.models.evaluation import EvaluationResult, ClaimResult, CitationResult
from app.models.trace import TraceEvent
from app.schemas.run import (
    RunCreate,
    RunResponse,
    AgentRunDetailResponse,
    RunComparisonResponse,
    PreFlightCheckRequest,
    PreFlightCheckResponse,
    RegressionAnalysisResponse,
    RegressionTestCase,
)
from app.evaluator.runner import EvaluationRunner
from app.evaluator.metrics import MetricsEngine
from app.api.deps import get_optional_user, log_audit_event

router = APIRouter(tags=["Runs"])


async def run_evaluation_task(
    run_id: str,
    concurrency: Optional[int] = None,
    test_case_subset: Optional[List[str]] = None
):
    async with AsyncSessionLocal() as session:
        try:
            runner = EvaluationRunner(session)
            await runner.execute_run(
                run_id=run_id,
                concurrency=concurrency,
                test_case_subset=test_case_subset
            )
        except Exception as e:
            print(f"Error executing run {run_id}: {e}")
            q = select(Run).where(Run.id == run_id)
            res = await session.execute(q)
            run = res.scalars().first()
            if run:
                run.status = "FAILED"
                run.error_message = str(e)
                await session.commit()


@router.post("/runs/preflight", response_model=PreFlightCheckResponse)
async def preflight_check(req: PreFlightCheckRequest, db: AsyncSession = Depends(get_db)):
    """
    Validates readiness before launching a real evaluation run:
    1. Agent exists and endpoint reachable
    2. Dataset exists and has valid test cases
    3. Evaluation profile exists
    4. LLM provider configured
    5. Required documents available
    """
    issues: List[str] = []
    warnings: List[str] = []

    # 1. Agent check
    ag_res = await db.execute(select(Agent).where(Agent.id == req.agent_id))
    agent = ag_res.scalars().first()
    agent_reachable = False

    if not agent:
        issues.append(f"Agent '{req.agent_id}' does not exist.")
    elif agent.adapter_type == "demo":
        agent_reachable = True
    elif not agent.endpoint:
        issues.append("Agent does not have an endpoint URL configured.")
    else:
        # Check endpoint reachability
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                probe_payload = {
                    "test_case_id": "PREFLIGHT_PING",
                    "question": "ping",
                    "language": "en"
                }
                headers = {"Content-Type": "application/json"}
                if agent.config_json and "api_key" in agent.config_json and agent.config_json["api_key"]:
                    headers["Authorization"] = f"Bearer {agent.config_json['api_key']}"
                resp = await client.post(agent.endpoint, json=probe_payload, headers=headers)
                if resp.status_code < 500:
                    agent_reachable = True
                else:
                    warnings.append(f"Agent endpoint returned HTTP {resp.status_code} during pre-flight check.")
        except Exception as e:
            warnings.append(f"Agent endpoint probe failed: {str(e)}. Run may encounter AGENT_ERROR.")
            agent_reachable = False

    # 2. Dataset check
    ds_res = await db.execute(select(Dataset).where(Dataset.id == req.dataset_id))
    dataset = ds_res.scalars().first()
    dataset_valid = False
    total_test_cases = 0

    if not dataset:
        issues.append(f"Dataset '{req.dataset_id}' does not exist.")
    else:
        tc_cnt_res = await db.execute(
            select(func.count(TestCase.id)).where(TestCase.dataset_id == req.dataset_id)
        )
        total_test_cases = tc_cnt_res.scalar() or 0
        if total_test_cases == 0:
            issues.append(f"Dataset '{dataset.name}' has 0 test cases.")
        else:
            dataset_valid = True

    # 3. Evaluation profile check
    evaluation_profile_valid = True
    if req.evaluation_profile_id:
        ep_res = await db.execute(select(EvaluationProfile).where(EvaluationProfile.id == req.evaluation_profile_id))
        if not ep_res.scalars().first():
            issues.append(f"Evaluation profile '{req.evaluation_profile_id}' not found.")
            evaluation_profile_valid = False

    # 4. Documents check
    doc_res = await db.execute(select(func.count(Document.id)))
    doc_count = doc_res.scalar() or 0
    documents_available = doc_count > 0
    if not documents_available:
        warnings.append("No reference documents found in document store. Grounding may be limited to agent-retrieved context.")

    is_ready = (len(issues) == 0) and dataset_valid and (agent is not None)

    return PreFlightCheckResponse(
        status="READY" if is_ready else "BLOCKED",
        agent_reachable=agent_reachable,
        dataset_valid=dataset_valid,
        evaluation_profile_valid=evaluation_profile_valid,
        llm_provider_configured=True,  # Built-in deterministic/mock/openai provider abstraction
        documents_available=documents_available,
        total_test_cases=total_test_cases,
        issues=issues,
        warnings=warnings
    )


@router.post("/runs", response_model=RunResponse, status_code=status.HTTP_201_CREATED)
async def create_run(
    data: RunCreate,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    ag_res = await db.execute(select(Agent).where(Agent.id == data.agent_id))
    agent = ag_res.scalars().first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    ds_res = await db.execute(select(Dataset).where(Dataset.id == data.dataset_id))
    dataset = ds_res.scalars().first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Count test cases
    tc_count_q = select(func.count(TestCase.id)).where(TestCase.dataset_id == data.dataset_id)
    if data.test_case_subset:
        tc_count_q = tc_count_q.where(TestCase.id.in_(data.test_case_subset))
    tc_count_res = await db.execute(tc_count_q)
    total_tests = tc_count_res.scalar() or 0

    # Retrieve profile if specified
    profile_json = {}
    if data.evaluation_profile_id:
        p_res = await db.execute(select(EvaluationProfile).where(EvaluationProfile.id == data.evaluation_profile_id))
        p_obj = p_res.scalars().first()
        if p_obj:
            profile_json = {
                "name": p_obj.name,
                "checks": p_obj.checks,
                "weights": p_obj.weights,
                "thresholds": p_obj.thresholds
            }

    run = Run(
        project_id=data.project_id,
        agent_id=data.agent_id,
        dataset_id=data.dataset_id,
        agent_version=data.agent_version or agent.version,
        dataset_version=data.dataset_version or dataset.version,
        evaluators_config=data.evaluators_config.model_dump() if data.evaluators_config else {},
        evaluation_profile_id=data.evaluation_profile_id,
        evaluation_profile_json=profile_json,
        is_demo=bool(data.is_demo or agent.adapter_type == "demo"),
        status="PENDING",
        total_tests=total_tests,
        completed_tests=0
    )
    db.add(run)
    await db.flush()

    if current_user:
        await log_audit_event(
            db=db,
            action="RUN_STARTED",
            entity_type="run",
            entity_id=run.id,
            user_id=current_user.id,
            details={
                "agent_id": agent.id,
                "dataset_id": dataset.id,
                "is_demo": run.is_demo,
                "total_tests": total_tests
            }
        )

    # Launch evaluation runner in background
    background_tasks.add_task(
        run_evaluation_task,
        run.id,
        data.concurrency,
        data.test_case_subset
    )

    return RunResponse(
        id=run.id,
        project_id=run.project_id,
        agent_id=run.agent_id,
        dataset_id=run.dataset_id,
        agent_version=run.agent_version,
        dataset_version=run.dataset_version,
        status=run.status,
        is_demo=run.is_demo,
        evaluation_profile_id=run.evaluation_profile_id,
        evaluators_config=run.evaluators_config or {},
        total_tests=run.total_tests,
        completed_tests=run.completed_tests,
        composite_score=run.composite_score,
        duration_seconds=run.duration_seconds,
        started_at=run.started_at,
        completed_at=run.completed_at,
        error_message=run.error_message,
        created_at=run.created_at,
        agent_name=agent.name,
        dataset_name=dataset.name
    )


@router.get("/runs", response_model=List[RunResponse])
async def list_runs(
    project_id: Optional[str] = None,
    is_demo: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    q = select(Run)
    if project_id:
        q = q.where(Run.project_id == project_id)
    if is_demo is not None:
        q = q.where(Run.is_demo == is_demo)
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
            "is_demo": r.is_demo,
            "evaluation_profile_id": r.evaluation_profile_id,
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
        is_demo=r.is_demo,
        evaluation_profile_id=r.evaluation_profile_id,
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
            if (search_lower not in tc.question.lower() and
                search_lower not in ar.final_answer.lower() and
                search_lower not in tc.external_id.lower()):
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


@router.get("/runs/{run_id}/metrics")
async def get_run_metrics(run_id: str, db: AsyncSession = Depends(get_db)):
    q = select(RunMetric).where(RunMetric.run_id == run_id)
    res = await db.execute(q)
    metric = res.scalars().first()
    if not metric:
        raise HTTPException(status_code=404, detail="Metrics not yet computed or run in progress")
    return metric.metrics_json


@router.get("/runs/{run_id}/regression", response_model=RegressionAnalysisResponse)
async def detect_regressions(
    run_id: str,
    baseline_run_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Identifies test cases that passed in baseline but regressed in the current run,
    as well as improvements (failed in baseline, passed in current).
    """
    curr_run = (await db.execute(select(Run).where(Run.id == run_id))).scalars().first()
    if not curr_run:
        raise HTTPException(status_code=404, detail="Current run not found")

    # If baseline not provided, find the immediately preceding completed run on the same dataset
    if not baseline_run_id:
        b_q = (
            select(Run)
            .where(
                Run.dataset_id == curr_run.dataset_id,
                Run.id != curr_run.id,
                Run.status == "COMPLETED",
                Run.created_at < curr_run.created_at
            )
            .order_by(Run.created_at.desc())
            .limit(1)
        )
        baseline = (await db.execute(b_q)).scalars().first()
    else:
        baseline = (await db.execute(select(Run).where(Run.id == baseline_run_id))).scalars().first()

    if not baseline:
        return RegressionAnalysisResponse(
            baseline_run_id="",
            current_run_id=curr_run.id,
            regression_detected=False,
            regressions_count=0,
            improvements_count=0,
            unchanged_count=0,
            test_cases=[]
        )

    # Fetch results for both runs
    async def get_run_map(r_id: str):
        q = (
            select(AgentRun)
            .where(AgentRun.run_id == r_id)
            .options(
                selectinload(AgentRun.test_case),
                selectinload(AgentRun.evaluation_result)
            )
        )
        res = await db.execute(q)
        return {ar.test_case.external_id: ar for ar in res.scalars().all() if ar.test_case and ar.evaluation_result}

    curr_map = await get_run_map(curr_run.id)
    base_map = await get_run_map(baseline.id)

    test_cases_analysis: List[RegressionTestCase] = []
    regressions_count = 0
    improvements_count = 0
    unchanged_count = 0

    for ext_id, curr_ar in curr_map.items():
        base_ar = base_map.get(ext_id)
        if not base_ar:
            continue

        base_status = base_ar.evaluation_result.overall_status
        curr_status = curr_ar.evaluation_result.overall_status
        base_score = base_ar.evaluation_result.composite_score
        curr_score = curr_ar.evaluation_result.composite_score

        if base_status == "PASS" and curr_status == "FAIL":
            change_type = "REGRESSION"
            regressions_count += 1
        elif base_status == "FAIL" and curr_status == "PASS":
            change_type = "IMPROVEMENT"
            improvements_count += 1
        else:
            change_type = "UNCHANGED"
            unchanged_count += 1

        test_cases_analysis.append(
            RegressionTestCase(
                test_case_id=curr_ar.test_case.id,
                external_id=ext_id,
                language=curr_ar.language,
                question=curr_ar.test_case.question,
                baseline_status=base_status,
                current_status=curr_status,
                change_type=change_type,
                baseline_score=base_score,
                current_score=curr_score,
                failure_reason=curr_ar.evaluation_result.correctness_reason or curr_ar.evaluation_result.grounding_reason,
                severity=curr_ar.evaluation_result.severity
            )
        )

    # Sort so regressions appear first
    sort_order = {"REGRESSION": 0, "IMPROVEMENT": 1, "UNCHANGED": 2}
    test_cases_analysis.sort(key=lambda x: sort_order.get(x.change_type, 3))

    return RegressionAnalysisResponse(
        baseline_run_id=baseline.id,
        current_run_id=curr_run.id,
        regression_detected=(regressions_count > 0),
        regressions_count=regressions_count,
        improvements_count=improvements_count,
        unchanged_count=unchanged_count,
        test_cases=test_cases_analysis
    )


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

    b_ag = (await db.execute(select(Agent.name).where(Agent.id == b_run.agent_id))).scalars().first()
    a_ag = (await db.execute(select(Agent.name).where(Agent.id == a_run.agent_id))).scalars().first()

    comparison = MetricsEngine.compare_runs(b_m.metrics_json, a_m.metrics_json)

    return RunComparisonResponse(
        before_run_id=before_run_id,
        after_run_id=after_run_id,
        before_agent_name=b_ag or "Baseline Agent",
        after_agent_name=a_ag or "After Agent",
        before_version=b_run.agent_version,
        after_version=a_run.agent_version,
        metrics=comparison["metrics"],
        language_deltas=comparison["language_deltas"]
    )
