import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config import settings
from app.models.run import Run, AgentRun, RunMetric
from app.models.trace import TraceEvent
from app.models.evaluation import EvaluationResult, ClaimResult, CitationResult
from app.models.agent import Agent
from app.models.dataset import TestCase
from app.agents.adapter import get_agent_adapter
from app.evaluator.orchestrator import EvaluationOrchestrator
from app.evaluator.metrics import MetricsEngine


class EvaluationRunner:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.orchestrator = EvaluationOrchestrator()

    async def execute_run(self, run_id: str) -> Run:
        """
        Executes an entire evaluation run asynchronously across all dataset test cases.
        Concurrent agent execution with synchronized database persistence.
        """
        # 1. Fetch Run, Agent, and TestCases
        q_run = select(Run).where(Run.id == run_id)
        res_run = await self.db.execute(q_run)
        run = res_run.scalars().first()
        if not run:
            raise ValueError(f"Run {run_id} not found.")

        q_agent = select(Agent).where(Agent.id == run.agent_id)
        res_agent = await self.db.execute(q_agent)
        agent = res_agent.scalars().first()
        if not agent:
            raise ValueError(f"Agent {run.agent_id} not found.")

        q_cases = select(TestCase).where(TestCase.dataset_id == run.dataset_id).order_by(TestCase.external_id)
        res_cases = await self.db.execute(q_cases)
        test_cases = res_cases.scalars().all()

        if not test_cases:
            run.status = "FAILED"
            run.error_message = "Dataset contains no test cases to evaluate."
            await self.db.commit()
            return run

        run.status = "RUNNING"
        run.started_at = datetime.now(timezone.utc)
        run.total_tests = len(test_cases)
        await self.db.commit()

        start_time = time.time()
        semaphore = asyncio.Semaphore(settings.MAX_CONCURRENCY)
        db_lock = asyncio.Lock()

        # Instantiate agent adapter
        adapter = get_agent_adapter(
            adapter_type=agent.adapter_type,
            endpoint=agent.endpoint,
            config=agent.config_json
        )

        evaluation_records: List[Dict[str, Any]] = []

        async def process_test_case(tc: TestCase):
            tc_dict = {
                "id": tc.external_id,
                "language": tc.language,
                "category": tc.category,
                "question": tc.question,
                "expected_answer": tc.expected_answer,
                "source_documents": tc.source_documents or [],
                "required_facts": tc.required_facts or [],
                "potential_traps": tc.potential_traps or []
            }

            # Step A: Run Agent Under Test (Concurrent)
            async with semaphore:
                agent_res = await adapter.run(tc_dict, config=agent.config_json)

                # Step B: Evaluate Observable Execution & Answer (Concurrent)
                eval_output = await self.orchestrator.evaluate_single(
                    test_case=tc_dict,
                    agent_result=agent_res.model_dump(),
                    evaluators_config=run.evaluators_config
                )

            # Step C: Synchronized Database Persistence (Thread-safe Async Lock)
            async with db_lock:
                agent_run = AgentRun(
                    run_id=run.id,
                    test_case_id=tc.id,
                    final_answer=agent_res.final_answer,
                    language=agent_res.language,
                    retrieved_documents=agent_res.retrieved_documents,
                    citations=agent_res.citations,
                    latency_ms=agent_res.latency_ms,
                    status=agent_res.status,
                    error_message=agent_res.error_message,
                    metadata_json=agent_res.metadata
                )
                self.db.add(agent_run)
                await self.db.flush()

                for t_ev in agent_res.trace:
                    trace_obj = TraceEvent(
                        agent_run_id=agent_run.id,
                        step=t_ev.get("step", 1),
                        event_type=t_ev.get("event_type", "generation"),
                        input_data=t_ev.get("input_data", {}),
                        output_data=t_ev.get("output_data", {}),
                        metadata_json=t_ev.get("metadata_json", {})
                    )
                    self.db.add(trace_obj)

                eval_res = EvaluationResult(
                    agent_run_id=agent_run.id,
                    run_id=run.id,
                    test_case_id=tc.id,
                    correctness_status=eval_output["correctness"]["status"],
                    correctness_score=eval_output["correctness"]["score"],
                    correctness_reason=eval_output["correctness"]["reason"],
                    deterministic_score=eval_output["correctness"]["deterministic_score"],
                    semantic_score=eval_output["correctness"]["semantic_score"],
                    grounding_status=eval_output["grounding"]["status"],
                    grounding_score=eval_output["grounding"]["score"],
                    grounding_reason=eval_output["grounding"]["reason"],
                    claims_count=eval_output["grounding"]["claims_count"],
                    supported_claims_count=eval_output["grounding"]["supported"],
                    unsupported_claims_count=eval_output["grounding"]["unsupported"],
                    contradicted_claims_count=eval_output["grounding"]["contradicted"],
                    citation_status=eval_output["citation"]["status"],
                    citation_score=eval_output["citation"]["score"],
                    citation_reason=eval_output["citation"]["reason"],
                    translation_status=eval_output["translation"]["status"],
                    translation_score=eval_output["translation"]["score"],
                    translation_reason=eval_output["translation"]["reason"],
                    back_translation=eval_output["translation"]["back_translation"],
                    trajectory_status=eval_output["trajectory"]["status"],
                    trajectory_score=eval_output["trajectory"]["score"],
                    trajectory_reason=eval_output["trajectory"]["reason"],
                    retrieval_executed=eval_output["trajectory"]["retrieval_executed"],
                    loop_detected=eval_output["trajectory"]["loop_detected"],
                    sequence_valid=eval_output["trajectory"]["sequence_valid"],
                    overall_status=eval_output["overall_status"],
                    composite_score=eval_output["composite_score"],
                    severity=eval_output["severity"],
                    raw_evaluation=eval_output
                )
                self.db.add(eval_res)
                await self.db.flush()

                for c in eval_output["grounding"].get("claims", []):
                    c_obj = ClaimResult(
                        evaluation_result_id=eval_res.id,
                        claim_text=c.get("claim", ""),
                        status=c.get("status", "SUPPORTED"),
                        document_id=c.get("document_id"),
                        section_id=c.get("section_id"),
                        evidence_text=c.get("evidence", ""),
                        reason=c.get("reason", "")
                    )
                    self.db.add(c_obj)

                for cit in eval_output["citation"].get("citations", []):
                    cit_obj = CitationResult(
                        evaluation_result_id=eval_res.id,
                        citation_text=cit.get("citation", ""),
                        status=cit.get("status", "VALID"),
                        document_id=cit.get("document_id"),
                        section_id=cit.get("section_id"),
                        evidence_matches=cit.get("evidence_matches", True),
                        reason=cit.get("reason", "")
                    )
                    self.db.add(cit_obj)

                evaluation_records.append(eval_output)
                run.completed_tests += 1

        # Execute tests concurrently with controlled concurrency
        tasks = [process_test_case(tc) for tc in test_cases]
        await asyncio.gather(*tasks)

        # Step G: Compute Overall Aggregate Metrics
        run_metrics = MetricsEngine.compute_run_metrics(evaluation_records)

        # Save RunMetric model
        metric_obj = RunMetric(
            run_id=run.id,
            metrics_json=run_metrics,
            language_metrics_json=run_metrics.get("language_breakdown", {})
        )
        self.db.add(metric_obj)

        # Complete Run
        duration_sec = round(time.time() - start_time, 2)
        run.status = "COMPLETED"
        run.completed_at = datetime.now(timezone.utc)
        run.duration_seconds = duration_sec
        run.composite_score = run_metrics.get("composite_score", 0.0)

        await self.db.commit()
        await self.db.refresh(run)
        return run
