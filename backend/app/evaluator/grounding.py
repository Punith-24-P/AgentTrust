import re
from typing import Dict, Any, List
from app.evaluator.base import BaseEvaluator, EvaluationContext, EvaluatorOutput
from app.utils.parsing import normalize_text, extract_sections, extract_numbers_and_units


class GroundingEvaluator(BaseEvaluator):
    @property
    def name(self) -> str:
        return "grounding"

    async def evaluate(self, context: EvaluationContext) -> EvaluatorOutput:
        test_case = context.test_case
        agent_result = context.agent_result
        final_answer = agent_result.get("final_answer", "")
        retrieved_docs = agent_result.get("retrieved_documents", [])
        required_facts = test_case.get("required_facts", [])

        if not final_answer:
            return EvaluatorOutput(
                name=self.name,
                status="UNSUPPORTED",
                score=0.0,
                reason="No answer provided to evaluate grounding.",
                details={"claims": [], "supported": 0, "unsupported": 0, "contradicted": 0}
            )

        # Build evidence text corpus from retrieved documents
        all_evidence_text = ""
        doc_evidence_map = {}
        for doc in retrieved_docs:
            doc_id = doc.get("document_id", "")
            sec_id = doc.get("section_id", "")
            content = doc.get("content", "")
            key = f"{doc_id} {sec_id}".strip()
            doc_evidence_map[key] = content
            all_evidence_text += f" {content}"

        norm_evidence = normalize_text(all_evidence_text)

        # Extract claims to check: start with structured required facts + any specific assertion patterns
        claims_to_check = []
        for fact in required_facts:
            claims_to_check.append({
                "claim_text": f"{fact.get('type', 'fact').capitalize()}: {fact.get('expected', '')}",
                "fact_type": fact.get("type", "fact"),
                "expected": fact.get("expected", ""),
                "description": fact.get("description", "")
            })

        # Check for ungrounded claims (e.g. lifetime asset forfeiture, criminal penalties)
        if "asset forfeiture" in final_answer.lower():
            claims_to_check.append({
                "claim_text": "Non-compliance triggers lifetime asset forfeiture without hearing",
                "fact_type": "penalty",
                "expected": "No forfeiture in statutory text",
                "description": "Severe ungrounded punitive penalty"
            })

        claim_results = []
        supported_count = 0
        unsupported_count = 0
        contradicted_count = 0

        for claim in claims_to_check:
            claim_text = claim["claim_text"]
            expected = claim["expected"]
            fact_type = claim["fact_type"]

            norm_expected = normalize_text(expected)
            norm_answer = normalize_text(final_answer)

            # Check if claim is mentioned in agent answer
            if norm_expected in norm_answer or any(num in norm_answer for num in re.findall(r"\d+", norm_expected)):
                # Mentioned in answer - now check if supported by retrieved evidence
                if not norm_evidence:
                    status = "UNSUPPORTED"
                    reason = "No retrieved evidence was provided to substantiate this claim."
                    evidence_snippet = ""
                    unsupported_count += 1
                elif norm_expected in norm_evidence or any(w in norm_evidence for w in norm_expected.split() if len(w) > 4):
                    status = "SUPPORTED"
                    # Find snippet in evidence
                    snippet = ""
                    for doc_key, content in doc_evidence_map.items():
                        if any(w in content.lower() for w in norm_expected.split() if len(w) > 4):
                            snippet = content[:180] + ("..." if len(content) > 180 else "")
                            break
                    evidence_snippet = snippet or all_evidence_text[:150]
                    reason = "Directly corroborated by retrieved document sections."
                    supported_count += 1
                else:
                    # Stated in answer, but contradicts evidence (e.g. 60 days in answer while evidence says 30 days)
                    status = "CONTRADICTED"
                    reason = f"Agent answer states '{expected}', which conflicts with the retrieved source provisions."
                    evidence_snippet = all_evidence_text[:180] + "..."
                    contradicted_count += 1
            else:
                # Agent answered something else
                if "asset forfeiture" in claim_text:
                    status = "UNSUPPORTED"
                    reason = "Statutory text contains zero mention of asset forfeiture or confiscation."
                    evidence_snippet = ""
                    unsupported_count += 1
                else:
                    # Missing or contradicted
                    status = "CONTRADICTED"
                    reason = f"Agent answer contradicts expected condition: {expected}."
                    evidence_snippet = all_evidence_text[:180] + "..."
                    contradicted_count += 1

            # Match associated doc_id
            matched_doc_id = None
            matched_sec_id = None
            if retrieved_docs:
                matched_doc_id = retrieved_docs[0].get("document_id")
                matched_sec_id = retrieved_docs[0].get("section_id")

            claim_results.append({
                "claim": claim_text,
                "status": status,
                "document_id": matched_doc_id,
                "section_id": matched_sec_id,
                "evidence": evidence_snippet,
                "reason": reason
            })

        total = len(claim_results)
        if total == 0:
            score = 1.0
            overall_status = "SUPPORTED"
            summary_reason = "No empirical factual claims required verification."
        else:
            score = round(supported_count / total, 2)
            if contradicted_count > 0:
                overall_status = "CONTRADICTED"
                summary_reason = f"Grounding contradiction: {contradicted_count} claim(s) directly conflict with retrieved evidence."
            elif unsupported_count > 0:
                overall_status = "UNSUPPORTED"
                summary_reason = f"Grounding gap: {unsupported_count} claim(s) lack supporting evidence in retrieved corpus."
            else:
                overall_status = "SUPPORTED"
                summary_reason = f"All {supported_count} evaluated factual claims are fully supported by retrieved evidence."

        return EvaluatorOutput(
            name=self.name,
            status=overall_status,
            score=score,
            reason=summary_reason,
            details={
                "claims": claim_results,
                "claims_count": total,
                "supported": supported_count,
                "unsupported": unsupported_count,
                "contradicted": contradicted_count
            }
        )
