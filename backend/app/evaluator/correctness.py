from typing import Dict, Any, List
from app.evaluator.base import BaseEvaluator, EvaluationContext, EvaluatorOutput
from app.utils.parsing import check_exact_fact
from app.services.llm import get_llm_provider


class CorrectnessEvaluator(BaseEvaluator):
    @property
    def name(self) -> str:
        return "correctness"

    def __init__(self):
        self.llm = get_llm_provider()

    async def evaluate(self, context: EvaluationContext) -> EvaluatorOutput:
        test_case = context.test_case
        agent_result = context.agent_result
        final_answer = agent_result.get("final_answer", "")
        expected_answer = test_case.get("expected_answer", "")
        required_facts = test_case.get("required_facts", [])

        if not final_answer:
            return EvaluatorOutput(
                name=self.name,
                status="FAIL",
                score=0.0,
                reason="Agent failed to produce an answer.",
                details={"deterministic_score": 0.0, "semantic_score": 0.0, "facts_checked": []}
            )

        # ----------------------------------------------------
        # Layer A: Deterministic Checks on Required Facts
        # ----------------------------------------------------
        fact_results = []
        passed_facts = 0
        total_facts = len(required_facts)

        for fact in required_facts:
            f_type = fact.get("type", "entity")
            f_exp = fact.get("expected", "")
            f_id = fact.get("id", "")
            status, reason = check_exact_fact(expected=f_exp, fact_type=f_type, actual_text=final_answer)
            if status == "PASS":
                passed_facts += 1

            fact_results.append({
                "fact_id": f_id,
                "type": f_type,
                "expected": f_exp,
                "status": status,
                "reason": reason
            })

        deterministic_score = (passed_facts / total_facts) if total_facts > 0 else 1.0

        # ----------------------------------------------------
        # Layer B: Semantic Meaning Evaluation (LLM Judge)
        # ----------------------------------------------------
        semantic_score = 1.0
        semantic_decision = "PASS"
        semantic_reason = "Answer conveys equivalent statutory meaning."

        if not self.llm.is_mock:
            try:
                prompt = (
                    f"You are an expert AI evaluator for legal and civic QA.\n"
                    f"Question: {test_case.get('question')}\n"
                    f"Expected Answer: {expected_answer}\n"
                    f"Agent Answer: {final_answer}\n"
                    f"Required Facts: {required_facts}\n\n"
                    f"Evaluate whether the Agent Answer is semantically correct and fulfills the requirements.\n"
                    f"Return JSON format: {{\"decision\": \"PASS|PARTIAL|FAIL\", \"semantic_score\": float between 0.0 and 1.0, \"reason\": \"string\"}}"
                )
                res = await self.llm.structured_generate(prompt=prompt)
                semantic_decision = res.get("decision", "PASS")
                semantic_score = float(res.get("semantic_score", 1.0))
                semantic_reason = res.get("reason", semantic_reason)
            except Exception as e:
                # Safe fallback, never crash
                semantic_reason = f"Semantic judge fallback (exception: {str(e)})"
                semantic_score = deterministic_score
        else:
            # Deterministic semantic inference
            if deterministic_score < 0.6:
                semantic_score = 0.3
                semantic_decision = "FAIL"
                semantic_reason = "Crucial statutory facts or deadlines are contradicted."
            elif deterministic_score < 1.0:
                semantic_score = 0.75
                semantic_decision = "PARTIAL"
                semantic_reason = "Some statutory details were omitted or mismatched."
            else:
                semantic_score = 1.0
                semantic_decision = "PASS"
                semantic_reason = "All required statutory conditions and facts are faithfully preserved."

        # Combined Score
        combined_score = round(0.5 * deterministic_score + 0.5 * semantic_score, 2)
        if combined_score >= 0.85:
            overall_status = "PASS"
            status_summary = "Correctness verified across deterministic facts and semantic judge."
        elif combined_score >= 0.60:
            overall_status = "PARTIAL"
            status_summary = f"Partial correctness: {passed_facts}/{total_facts} required facts verified."
        else:
            overall_status = "FAIL"
            failed_facts = [f for f in fact_results if f['status'] != 'PASS']
            reasons = "; ".join([f"{f['expected']}: {f['reason']}" for f in failed_facts[:2]])
            status_summary = f"Correctness failure: {reasons}"

        return EvaluatorOutput(
            name=self.name,
            status=overall_status,
            score=combined_score,
            reason=status_summary,
            details={
                "deterministic_score": deterministic_score,
                "semantic_score": semantic_score,
                "semantic_decision": semantic_decision,
                "semantic_reason": semantic_reason,
                "facts_checked": fact_results
            }
        )
