from typing import Dict, Any, List
from app.evaluator.base import BaseEvaluator, EvaluationContext, EvaluatorOutput


class TrajectoryEvaluator(BaseEvaluator):
    @property
    def name(self) -> str:
        return "trajectory"

    async def evaluate(self, context: EvaluationContext) -> EvaluatorOutput:
        test_case = context.test_case
        agent_result = context.agent_result
        trace = agent_result.get("trace", [])
        source_docs = test_case.get("source_documents", [])
        requires_retrieval = len(source_docs) > 0

        if not trace:
            return EvaluatorOutput(
                name=self.name,
                status="FAIL",
                score=0.0,
                reason="No observable trace events recorded during execution.",
                details={"retrieval_executed": False, "loop_detected": False, "sequence_valid": False}
            )

        # 1. Inspect Event Types and Sequence
        event_types = [e.get("event_type") for e in trace]
        retrieval_indices = [i for i, et in enumerate(event_types) if et == "retrieval"]
        generation_indices = [i for i, et in enumerate(event_types) if et == "generation"]
        tool_call_indices = [i for i, et in enumerate(event_types) if et == "tool_call"]
        error_events = [e for e in trace if e.get("event_type") == "error"]

        retrieval_executed = len(retrieval_indices) > 0

        # Check loop anomalies: same tool or retrieval called consecutively with identical parameters
        loop_detected = False
        loop_reason = ""
        for i in range(len(trace) - 1):
            curr_e = trace[i]
            next_e = trace[i + 1]
            if curr_e.get("event_type") == next_e.get("event_type") == "retrieval":
                loop_detected = True
                loop_reason = "Redundant consecutive document retrieval loop detected without query refinement."
                break

        # Check sequence validity: retrieval before generation
        sequence_valid = True
        sequence_reason = "Valid linear execution sequence."
        if requires_retrieval and retrieval_executed and generation_indices:
            if min(generation_indices) < max(retrieval_indices):
                sequence_valid = False
                sequence_reason = "Answer generation initiated prior to conclusion of document retrieval."

        # Compute Score and Status
        warnings = []
        failures = []

        if requires_retrieval and not retrieval_executed:
            failures.append("Expected document retrieval step was bypassed.")

        if error_events:
            failures.append(f"Execution terminated with error event: {error_events[0].get('output_data')}")

        if not sequence_valid:
            warnings.append(sequence_reason)

        if loop_detected:
            warnings.append(loop_reason)

        if failures:
            status = "FAIL"
            score = 0.20
            summary_reason = f"Trajectory failure: {'; '.join(failures)}"
        elif warnings:
            status = "WARNING"
            score = 0.70
            summary_reason = f"Trajectory warning: {'; '.join(warnings)}"
        else:
            status = "PASS"
            score = 1.0
            summary_reason = "Observable execution followed an optimal, valid tool and retrieval sequence."

        return EvaluatorOutput(
            name=self.name,
            status=status,
            score=score,
            reason=summary_reason,
            details={
                "retrieval_executed": retrieval_executed,
                "loop_detected": loop_detected,
                "sequence_valid": sequence_valid,
                "total_steps": len(trace),
                "warnings": warnings,
                "failures": failures
            }
        )
