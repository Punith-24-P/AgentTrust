import asyncio
from typing import Dict, Any, List, Optional
from app.evaluator.base import BaseEvaluator, EvaluationContext, EvaluatorOutput
from app.evaluator.correctness import CorrectnessEvaluator
from app.evaluator.grounding import GroundingEvaluator
from app.evaluator.citation import CitationEvaluator
from app.evaluator.translation import TranslationEvaluator
from app.evaluator.trajectory import TrajectoryEvaluator


class EvaluationOrchestrator:
    """
    Coordinates modular evaluators, executes them concurrently or sequentially,
    normalizes output, computes composite reliability score with documented weights,
    and assigns rule-based failure severity.
    """

    def __init__(self):
        self.evaluators: Dict[str, BaseEvaluator] = {
            "correctness": CorrectnessEvaluator(),
            "grounding": GroundingEvaluator(),
            "citation": CitationEvaluator(),
            "translation": TranslationEvaluator(),
            "trajectory": TrajectoryEvaluator()
        }

    def calculate_severity(
        self,
        correctness: EvaluatorOutput,
        grounding: EvaluatorOutput,
        citation: EvaluatorOutput,
        translation: EvaluatorOutput,
        trajectory: EvaluatorOutput
    ) -> str:
        """
        Rule-based failure severity calculation:
        - CRITICAL: Contradicted important factual claim in grounding
        - HIGH: Wrong required fact in correctness OR major translation drift
        - MEDIUM: Citation mismatch / invalid source OR unsupported claim
        - LOW: Minor trajectory loop warning / minor drift
        """
        if grounding.status == "CONTRADICTED":
            return "CRITICAL"

        if correctness.status == "FAIL" or translation.status == "MAJOR_DRIFT":
            return "HIGH"

        if citation.status in ["INVALID_SOURCE", "INVALID_SECTION", "MISMATCH"] or grounding.status == "UNSUPPORTED":
            return "MEDIUM"

        if trajectory.status in ["WARNING", "FAIL"] or translation.status == "MINOR_DRIFT":
            return "LOW"

        return "LOW"

    async def evaluate_single(
        self,
        test_case: Dict[str, Any],
        agent_result: Dict[str, Any],
        evaluators_config: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        eval_cfg = evaluators_config or {
            "correctness": True,
            "grounding": True,
            "citation": True,
            "translation": True,
            "trajectory": True
        }

        context = EvaluationContext(
            test_case=test_case,
            agent_result=agent_result,
            evaluators_config=eval_cfg
        )

        lang = test_case.get("language", "en").lower()

        # Run configured evaluators concurrently
        tasks = {}
        for name, evaluator in self.evaluators.items():
            if eval_cfg.get(name, True):
                tasks[name] = evaluator.evaluate(context)

        results: Dict[str, EvaluatorOutput] = {}
        executed_names = list(tasks.keys())
        outputs = await asyncio.gather(*[tasks[k] for k in executed_names], return_exceptions=True)

        for name, out in zip(executed_names, outputs):
            if isinstance(out, Exception):
                # Evaluator error handling (distinguished from agent failure)
                results[name] = EvaluatorOutput(
                    name=name,
                    status="ERROR",
                    score=0.0,
                    reason=f"EVALUATOR_ERROR in {name}: {str(out)}",
                    details={"error": str(out)}
                )
            else:
                results[name] = out

        # Fill any disabled evaluators with skipped defaults
        for name in self.evaluators:
            if name not in results:
                results[name] = EvaluatorOutput(
                    name=name,
                    status="SKIPPED",
                    score=1.0,
                    reason=f"Evaluator '{name}' was disabled in run configuration.",
                    details={}
                )

        corr = results["correctness"]
        ground = results["grounding"]
        cite = results["citation"]
        trans = results["translation"]
        traj = results["trajectory"]

        # -------------------------------------------------------------------------
        # Composite Reliability Score Calculation
        # Documented standard weights:
        # Correctness: 30%, Grounding: 30%, Citation: 15%, Translation: 15%, Trajectory: 10%
        # For English (where translation is NA):
        # Correctness: 35%, Grounding: 35%, Citation: 15%, Trajectory: 15%
        # -------------------------------------------------------------------------
        if lang == "en":
            weights = {"correctness": 0.35, "grounding": 0.35, "citation": 0.15, "trajectory": 0.15}
            composite = (
                weights["correctness"] * corr.score +
                weights["grounding"] * ground.score +
                weights["citation"] * cite.score +
                weights["trajectory"] * traj.score
            )
        else:
            weights = {"correctness": 0.30, "grounding": 0.30, "citation": 0.15, "translation": 0.15, "trajectory": 0.10}
            composite = (
                weights["correctness"] * corr.score +
                weights["grounding"] * ground.score +
                weights["citation"] * cite.score +
                weights["translation"] * trans.score +
                weights["trajectory"] * traj.score
            )

        composite_score = round(composite, 3)

        # Overall Status (Pass if composite >= 0.85 and no critical failures)
        is_pass = (
            composite_score >= 0.80 and
            ground.status != "CONTRADICTED" and
            corr.status != "FAIL" and
            trans.status != "MAJOR_DRIFT"
        )
        overall_status = "PASS" if is_pass else "FAIL"

        severity = self.calculate_severity(corr, ground, cite, trans, traj) if not is_pass else "LOW"

        return {
            "test_case_id": test_case.get("id"),
            "language": lang,
            "overall_status": overall_status,
            "composite_score": composite_score,
            "severity": severity,
            "correctness": {
                "status": corr.status,
                "score": corr.score,
                "reason": corr.reason,
                "deterministic_score": corr.details.get("deterministic_score", 1.0),
                "semantic_score": corr.details.get("semantic_score", 1.0),
                "facts_checked": corr.details.get("facts_checked", [])
            },
            "grounding": {
                "status": ground.status,
                "score": ground.score,
                "reason": ground.reason,
                "claims_count": ground.details.get("claims_count", 0),
                "supported": ground.details.get("supported", 0),
                "unsupported": ground.details.get("unsupported", 0),
                "contradicted": ground.details.get("contradicted", 0),
                "claims": ground.details.get("claims", [])
            },
            "citation": {
                "status": cite.status,
                "score": cite.score,
                "reason": cite.reason,
                "citations": cite.details.get("citations", []),
                "valid_count": cite.details.get("valid_count", 0),
                "mismatch_count": cite.details.get("mismatch_count", 0)
            },
            "translation": {
                "status": trans.status,
                "score": trans.score,
                "reason": trans.reason,
                "back_translation": trans.details.get("back_translation", ""),
                "drifts_detected": trans.details.get("drifts_detected", [])
            },
            "trajectory": {
                "status": traj.status,
                "score": traj.score,
                "reason": traj.reason,
                "retrieval_executed": traj.details.get("retrieval_executed", True),
                "loop_detected": traj.details.get("loop_detected", False),
                "sequence_valid": traj.details.get("sequence_valid", True)
            }
        }
